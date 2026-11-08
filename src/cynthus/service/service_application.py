"""Service application for the Cynthus project"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from cynthus.core import RedisClient, logging
from cynthus.messaging.publisher import ServiceBusSignalPublisher
from cynthus.messaging.subscriber import ServiceBusSignalSubscriber
from cynthus.security import SignalAccessRecorder, TokenVerifier

from .service_bus_connection import ServiceBusConnection

LOGGER = logging.getLogger(__name__)


class ServiceApplication:
    """
        Builds the FastAPI application every domain service shares

        The service supplies its name, its routers, the subscription it listens on and a handler. This class does the
        rest: it opens the Redis client and the one Service Bus connection, turns every access decision into an audit
        signal, runs the subscriber for the life of the application, and closes everything on shutdown. It adds the
        index route and ``/signal/health``.

        ``handler(signal, publisher)`` is called with each `ReceivedSignal` and the `ServiceBusSignalPublisher` that
        shares the service's connection. A handler that raises sends its signal to the dead-letter queue.
    """

    def __init__(self, name: str, routers, subscription, handler, signal_access=None, database=None) -> None:
        self.name = name
        self._routers = list(routers)
        self._subscription = subscription
        self._handler = handler
        self._signal_access = signal_access
        self._database = database

    def initialize(self) -> FastAPI:
        logger = LOGGER.getChild('initialize')

        logger.info('Starting the %s application...', self.name)

        application = FastAPI(lifespan=self._lifespan)

        for router in self._routers:
            application.include_router(router)

        application.include_router(self._system_router())

        logger.info('The %s application has been initialized', self.name)

        return application

    def _system_router(self) -> APIRouter:
        router = APIRouter()
        subscription = self._subscription

        @router.get('/')
        async def get_index():
            return {}

        @router.get('/signal/health')
        async def get_signal_health():
            """Lightweight readiness probe for the signal subscriber."""

            return {'subscription': subscription.name, 'topic': subscription.topic.name}

        return router

    @asynccontextmanager
    async def _lifespan(self, application: FastAPI):
        logger = LOGGER.getChild('_lifespan')

        logger.info('Configuring lifespan for the %s application...', self.name)

        redis = RedisClient.from_environment()
        connection = ServiceBusConnection.from_environment()
        publisher = ServiceBusSignalPublisher.for_client(connection.client)

        # Every access decision becomes an audit signal; the publisher shares this service's bus connection
        recorder = SignalAccessRecorder(publisher)

        if self._signal_access is not None:
            self._signal_access.recorder = recorder

        application.state.redis = redis
        application.state.token_verifier = TokenVerifier.from_environment()
        application.state.access_recorder = recorder
        application.state.service_bus = connection.client
        application.state.signal_publisher = publisher

        subscriber = ServiceBusSignalSubscriber(connection.client)
        subscriber.subscribe(self._subscription.topic, self._subscription.name, self._handle(publisher))

        task = asyncio.create_task(subscriber.run())
        application.state.signal_task = task

        yield

        logger.info('Starting the teardown process in the %s application lifecycle...', self.name)

        await self._stop(task)
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
