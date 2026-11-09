"""Service application for the Cynthus project"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from cynthus.core import RedisClient, logging
from cynthus.messaging.publisher import ServiceBusSignalPublisher, SignalBusUnavailable
from cynthus.messaging.subscriber import ServiceBusSignalSubscriber
from cynthus.security import SignalAccessRecorder, TokenVerifier

from .service_bus_connection import ServiceBusConnection
from .signal_bus_unavailable_handler import signal_bus_unavailable_handler

LOGGER = logging.getLogger(__name__)


class ServiceApplication:
    """
        Builds the FastAPI application every domain service shares

        The service supplies its name, its routers, the subscription it listens on and a handler. This class does the
        rest: it opens the Redis client and the one Service Bus connection, turns every access decision into an audit
        signal, runs the subscriber for the life of the application, and closes everything on shutdown. It adds the
        index route and ``/signal/health``, which answers 503 while the subscriber is not running or the database does
        not answer.

        ``handler(signal, publisher)`` is called with each `ReceivedSignal` and the `ServiceBusSignalPublisher` that
        shares the service's connection. A handler that raises sends its signal to the dead-letter queue.

        A request that fails because the bus is down (`SignalBusUnavailable`) is answered with 503 and `Retry-After`.

        A service that has no bus (for example the Session gateway) leaves out ``subscription`` and ``handler``: it
        then gets the Redis client, the token verifier and the index route, and no Service Bus connection.

        ``startup(application)`` runs once the shared parts are open (so it can use ``application.state.redis``) and
        may add the service's own clients to ``application.state``. ``shutdown(application)`` runs after the
        subscriber has stopped and before the shared parts close.
    """

    def __init__(
        self, name: str, routers, subscription=None, handler=None, signal_access=None, database=None,
        startup=None, shutdown=None,
    ) -> None:
        if (subscription is None) != (handler is None):
            raise ValueError('a subscription and its handler go together: give both or neither')

        self.name = name
        self._routers = list(routers)
        self._subscription = subscription
        self._handler = handler
        self._signal_access = signal_access
        self._database = database
        self._startup = startup
        self._shutdown = shutdown

    def initialize(self) -> FastAPI:
        logger = LOGGER.getChild('initialize')

        logger.info('Starting the %s application...', self.name)

        application = FastAPI(lifespan=self._lifespan)
        application.add_exception_handler(SignalBusUnavailable, signal_bus_unavailable_handler)

        for router in self._routers:
            application.include_router(router)

        application.include_router(self._system_router())

        if self._subscription is not None:
            application.include_router(self._signal_router())

        logger.info('The %s application has been initialized', self.name)

        return application

    def _system_router(self) -> APIRouter:
        router = APIRouter()

        @router.get('/')
        async def get_index():
            return {}

        return router

    def _signal_router(self) -> APIRouter:
        router = APIRouter()
        subscription = self._subscription
        database = self._database

        @router.get('/signal/health')
        async def get_signal_health(request: Request):
            """Ready only while the signal subscriber is running and the database answers; otherwise 503 with the reason."""

            health = {'subscription': subscription.name, 'topic': subscription.topic.name}
            task = getattr(request.app.state, 'signal_task', None)

            if task is None or task.done():
                return JSONResponse(
                    {**health, 'status': 'unavailable', 'reason': 'the signal subscriber is not running'}, 503
                )

            if database is not None:
                try:
                    async with database.session() as session:
                        await session.execute(text('SELECT 1'))
                except Exception:
                    LOGGER.getChild('get_signal_health').exception('The database did not answer')

                    return JSONResponse(
                        {**health, 'status': 'unavailable', 'reason': 'the database is not reachable'}, 503
                    )

            return {**health, 'status': 'ok'}

        return router

    @asynccontextmanager
    async def _lifespan(self, application: FastAPI):
        logger = LOGGER.getChild('_lifespan')

        logger.info('Configuring lifespan for the %s application...', self.name)

        redis = RedisClient.from_environment()
        connection = publisher = task = None

        application.state.redis = redis
        application.state.token_verifier = TokenVerifier.from_environment()

        if self._subscription is not None:
            connection = ServiceBusConnection.from_environment()
            publisher = ServiceBusSignalPublisher.for_client(connection.client)

            # Every access decision becomes an audit signal; the publisher shares this service's bus connection
            recorder = SignalAccessRecorder(publisher)

            if self._signal_access is not None:
                self._signal_access.recorder = recorder

            application.state.access_recorder = recorder
            application.state.service_bus = connection.client
            application.state.signal_publisher = publisher

            subscriber = ServiceBusSignalSubscriber(connection.client)
            subscriber.subscribe(self._subscription.topic, self._subscription.name, self._handle(publisher))

            task = asyncio.create_task(subscriber.run())
            application.state.signal_task = task

        if self._startup is not None:
            await self._startup(application)

        yield

        logger.info('Starting the teardown process in the %s application lifecycle...', self.name)

        if task is not None:
            await self._stop(task)

        if self._shutdown is not None:
            await self._close(lambda: self._shutdown(application), 'the service')

        if publisher is not None:
            await self._close(publisher.close, 'the signal publisher')
            await self._close(connection.close, 'the Service Bus connection')

        await self._close(redis.close, 'the Redis client')

        if self._database is not None:
            await self._close(self._database.dispose, 'the database')

    def _handle(self, publisher):
        async def handle(signal) -> None:
            await self._handler(signal, publisher)

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
