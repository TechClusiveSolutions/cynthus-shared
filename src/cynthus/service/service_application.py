"""Service application for the Cynthus project"""

import asyncio
from contextlib import asynccontextmanager
from os import environ

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from cynthus.core import RedisClient, logging
from cynthus.messaging.publisher import SignalBusUnavailable
from cynthus.security import SignalAccessRecorder, TokenVerifier

from .service_module import ServiceModule
from .service_outage import ServiceOutage
from .signal_broker import SignalBroker
from .signal_bus_unavailable_handler import signal_bus_unavailable_handler

LOGGER = logging.getLogger(__name__)

# A handler that has not finished after this many seconds is cancelled and its signal is dead-lettered, so one module cannot
# hold up the others that share its event loop. 0 turns the limit off.
HANDLER_TIMEOUT_SETTING = 'SIGNAL_HANDLER_TIMEOUT_SECONDS'
DEFAULT_HANDLER_TIMEOUT_SECONDS = 60.0


class ServiceApplication:
    """
        Builds the FastAPI application every domain service shares

        The service supplies its name, its routers, the subscription it listens on and a handler. This class does the
        rest: it opens the Redis client and the one broker connection (Service Bus or RabbitMQ, per ``SIGNAL_BROKER``), turns every access decision into an audit
        signal, runs the subscriber for the life of the application, and closes everything on shutdown. It adds the
        index route and ``/signal/health``, which answers 503 while the subscriber is not running or the database does
        not answer.

        ``handler(signal, publisher)`` is called with each `ReceivedSignal` and the `ServiceBusSignalPublisher` that
        shares the service's connection. A handler that raises sends its signal to the dead-letter queue.

        A request that fails because the bus is down (`SignalBusUnavailable`) is answered with 503 and `Retry-After`,
        and the service records the outage in Redis (`ServiceOutage`) while it lasts.

        A service that has no bus (for example the Session gateway) leaves out ``subscription`` and ``handler``: it
        then gets the Redis client, the token verifier and the index route, and no Service Bus connection.

        An application can host several modules (`ServiceModule`, ADR-008): ``ServiceApplication(name, modules=[...])``.
        It opens Redis, the token verifier and the broker once, subscribes every module, and runs one subscriber.
        ``/signal/health`` then lists the modules and answers 503 if any is unavailable; ``/signal/health/{module}``
        answers for one. A handler that runs longer than ``SIGNAL_HANDLER_TIMEOUT_SECONDS`` (default 60, 0 for no limit) is
        cancelled and its signal is dead-lettered.

        ``startup(application)`` runs once the shared parts are open (so it can use ``application.state.redis``) and
        may add the service's own clients to ``application.state``. ``shutdown(application)`` runs after the
        subscriber has stopped and before the shared parts close.
    """

    def __init__(
        self, name: str, routers=(), subscription=None, handler=None, signal_access=None, database=None,
        startup=None, shutdown=None, modules=None,
    ) -> None:
        if modules is not None:
            given = (routers, subscription, handler, signal_access, database, startup, shutdown)

            if any(value for value in given):
                raise ValueError('give either modules or the single-module arguments, not both')

            modules = list(modules)

            if not modules:
                raise ValueError('modules must name at least one module')

            names = [module.name for module in modules]

            if len(set(names)) != len(names):
                raise ValueError(f'module names must be different: {", ".join(names)}')
        else:
            modules = [ServiceModule(name, routers, subscription, handler, signal_access, database, startup, shutdown)]

        self.name = name
        self._modules = modules
        self._handler_timeout = self._timeout_from_environment()

    @staticmethod
    def _timeout_from_environment() -> float | None:
        raw = (environ.get(HANDLER_TIMEOUT_SETTING) or '').strip()

        if not raw:
            return DEFAULT_HANDLER_TIMEOUT_SECONDS

        try:
            seconds = float(raw)
        except ValueError:
            seconds = -1

        if seconds < 0:
            raise ValueError(f'{HANDLER_TIMEOUT_SETTING} must be a number of seconds, 0 or more; it is {raw!r}')

        return seconds or None

    def initialize(self) -> FastAPI:
        logger = LOGGER.getChild('initialize')

        logger.info('Starting the %s application...', self.name)

        application = FastAPI(lifespan=self._lifespan)
        application.add_exception_handler(SignalBusUnavailable, signal_bus_unavailable_handler)

        for module in self._modules:
            for router in module.routers:
                application.include_router(router)

        application.include_router(self._system_router())

        if self._bus_modules():
            application.include_router(self._signal_router())

        logger.info('The %s application has been initialized', self.name)

        return application

    def _system_router(self) -> APIRouter:
        router = APIRouter()

        @router.get('/')
        async def get_index():
            return {}

        return router

    def _bus_modules(self) -> list:
        return [module for module in self._modules if module.subscription is not None]

    def _signal_router(self) -> APIRouter:
        router = APIRouter()
        bus_modules = self._bus_modules()
        single = len(self._modules) == 1

        @router.get('/signal/health')
        async def get_signal_health(request: Request):
            """Ready only while the signal subscriber is running and every database answers; otherwise 503 with the reason."""

            results = {module.name: await self._module_health(module, request) for module in bus_modules}

            if single:
                status, body = results[bus_modules[0].name]

                return body if status == 200 else JSONResponse(body, status)

            ready = all(status == 200 for status, _ in results.values())
            body = {
                'status': 'ok' if ready else 'unavailable',
                'modules': {name: module_body for name, (_, module_body) in results.items()},
            }

            return body if ready else JSONResponse(body, 503)

        @router.get('/signal/health/{module}')
        async def get_module_signal_health(module: str, request: Request):
            """The same check for one module."""

            chosen = next((candidate for candidate in bus_modules if candidate.name == module), None)

            if chosen is None:
                return JSONResponse({'error': f'there is no module named {module}'}, 404)

            status, body = await self._module_health(chosen, request)

            return body if status == 200 else JSONResponse(body, status)

        return router

    async def _module_health(self, module: ServiceModule, request: Request) -> tuple:
        subscription = module.subscription
        health = {'subscription': subscription.name, 'topic': subscription.topic.name}
        task = getattr(request.app.state, 'signal_task', None)

        if task is None or task.done():
            return 503, {**health, 'status': 'unavailable', 'reason': 'the signal subscriber is not running'}

        if module.database is not None:
            try:
                async with module.database.session() as session:
                    await session.execute(text('SELECT 1'))
            except Exception:
                LOGGER.getChild('_module_health').exception('The database of the %s module did not answer', module.name)

                return 503, {**health, 'status': 'unavailable', 'reason': 'the database is not reachable'}

        return 200, {**health, 'status': 'ok'}

    @asynccontextmanager
    async def _lifespan(self, application: FastAPI):
        logger = LOGGER.getChild('_lifespan')

        logger.info('Configuring lifespan for the %s application...', self.name)

        redis = RedisClient.from_environment()
        broker = publisher = task = None

        application.state.redis = redis
        application.state.token_verifier = TokenVerifier.from_environment()

        bus_modules = self._bus_modules()

        if bus_modules:
            broker = SignalBroker.from_environment()
            publisher = broker.publisher

            # Every access decision becomes an audit signal; the publisher shares this service's bus connection
            recorder = SignalAccessRecorder(publisher)

            for module in bus_modules:
                if module.signal_access is not None:
                    module.signal_access.recorder = recorder

            application.state.access_recorder = recorder

            # When the bus cannot be reached, say so in Redis for the Session service (and so the web and the mobile app)
            application.state.outage = ServiceOutage(redis)
            publisher.on_unavailable = application.state.outage.report
            application.state.service_bus = broker.client
            application.state.signal_publisher = publisher

            subscriber = broker.subscriber

            for module in bus_modules:
                subscriber.subscribe(
                    module.subscription.topic, module.subscription.name, self._handle(module, publisher)
                )

            task = asyncio.create_task(subscriber.run())
            application.state.signal_task = task

        for module in self._modules:
            if module.startup is not None:
                await module.startup(application)

        yield

        logger.info('Starting the teardown process in the %s application lifecycle...', self.name)

        if task is not None:
            await self._stop(task)

        for module in reversed(self._modules):
            if module.shutdown is not None:
                await self._close(lambda module=module: module.shutdown(application), f'the {module.name} service')

        if broker is not None:
            await self._close(broker.close, 'the signal broker')

        await self._close(redis.close, 'the Redis client')

        for module in self._modules:
            if module.database is not None:
                await self._close(module.database.dispose, f'the {module.name} database')

    def _handle(self, module: ServiceModule, publisher):
        timeout = self._handler_timeout

        async def handle(signal) -> None:
            try:
                await asyncio.wait_for(module.handler(signal, publisher), timeout)
            except asyncio.TimeoutError as error:
                # Raising dead-letters this one signal; the signals behind it, and the other modules, carry on
                raise TimeoutError(f'The {module.name} handler did not finish within {timeout:g} seconds') from error

        return handle

    async def _stop(self, task) -> None:
        logger = LOGGER.getChild('_stop')

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            logger.debug('The signal subscriber of the %s application was cancelled', self.name)
        except Exception:
            logger.exception('The signal subscriber of the %s application raised during shutdown', self.name)

    async def _close(self, close, what: str) -> None:
        try:
            await close()
        except Exception:
            LOGGER.getChild('_close').exception('Closing %s of the %s application failed', what, self.name)
