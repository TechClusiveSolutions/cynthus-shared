"""Tests for cynthus.service.service_application (ServiceApplication)."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from cynthus.messaging.subscriber import ReceivedSignal
from cynthus.messaging.subscription import CoreRecipeSignalSubscription
from cynthus.service import ServiceApplication
from cynthus.service import service_application as module


class Parts:
    """Everything the application would open, replaced by fakes."""

    def __init__(self):
        self.redis = MagicMock()
        self.redis.close = AsyncMock()

        self.client = MagicMock()
        self.connection = MagicMock(client=self.client)
        self.connection.close = AsyncMock()

        self.publisher = MagicMock()
        self.publisher.close = AsyncMock()

        self.verifier = MagicMock()

        self.stopped = asyncio.Event()
        self.subscriber = MagicMock()
        self.subscriber.run = AsyncMock(side_effect=self._forever)

    async def _forever(self):
        try:
            await asyncio.Event().wait()
        finally:
            self.stopped.set()


@pytest.fixture
def parts():
    fakes = Parts()

    with patch.object(module.RedisClient, 'from_environment', return_value=fakes.redis), \
            patch.object(module.ServiceBusConnection, 'from_environment', return_value=fakes.connection), \
            patch.object(module.ServiceBusSignalPublisher, 'for_client', return_value=fakes.publisher), \
            patch.object(module.TokenVerifier, 'from_environment', return_value=fakes.verifier), \
            patch.object(module, 'ServiceBusSignalSubscriber', return_value=fakes.subscriber):
        yield fakes


async def handler(signal, publisher):
    return None


def build(**overrides):
    values = dict(name='Recipe', routers=[], subscription=CoreRecipeSignalSubscription(), handler=handler)
    values.update(overrides)

    return ServiceApplication(**values)


def test_the_routers_and_the_system_routes_are_mounted(parts):
    router = APIRouter()

    @router.get('/thing')
    async def thing():
        return {'thing': True}

    with TestClient(build(routers=[router]).initialize()) as client:
        assert client.get('/thing').json() == {'thing': True}
        assert client.get('/').json() == {}
        assert client.get('/signal/health').json() == {
            'subscription': 'cynthus-sub-core-recipe', 'topic': 'cynthus-events-topic', 'status': 'ok'}


def test_startup_opens_what_the_service_needs_and_records_access_as_signals(parts):
    access = SimpleNamespace(recorder=None)

    with patch.object(module, 'SignalAccessRecorder') as recorder_class:
        application = build(signal_access=access).initialize()

        with TestClient(application):
            recorder_class.assert_called_once_with(parts.publisher)
            assert access.recorder is recorder_class.return_value
            assert application.state.redis is parts.redis
            assert application.state.token_verifier is parts.verifier
            assert application.state.access_recorder is recorder_class.return_value
            assert application.state.service_bus is parts.client
            assert application.state.signal_publisher is parts.publisher


def test_startup_works_without_a_signal_access_object(parts):
    with TestClient(build().initialize()):
        pass


def test_the_subscriber_listens_on_the_subscription_with_the_shared_client(parts):
    with patch.object(module, 'ServiceBusSignalSubscriber', return_value=parts.subscriber) as subscriber_class:
        with TestClient(build().initialize()):
            subscriber_class.assert_called_once_with(parts.client)

    topic, name, _ = parts.subscriber.subscribe.call_args.args

    assert topic.name == 'cynthus-events-topic'
    assert name == 'cynthus-sub-core-recipe'
    parts.subscriber.run.assert_awaited_once()


def test_the_handler_gets_each_signal_with_the_publisher(parts):
    seen = []

    async def recording(signal, publisher):
        seen.append((signal, publisher))

    with TestClient(build(handler=recording).initialize()):
        registered = parts.subscriber.subscribe.call_args.args[2]
        signal = ReceivedSignal(event_type='a.b.c', body='{}')

        asyncio.run(registered(signal))

    assert seen == [(signal, parts.publisher)]


def test_shutdown_stops_the_subscriber_and_closes_everything(parts):
    database = MagicMock()
    database.dispose = AsyncMock()

    with TestClient(build(database=database).initialize()):
        pass

    assert parts.stopped.is_set()
    parts.publisher.close.assert_awaited_once()
    parts.connection.close.assert_awaited_once()
    parts.redis.close.assert_awaited_once()
    database.dispose.assert_awaited_once()


def test_a_failure_while_closing_one_thing_does_not_stop_the_others(parts):
    parts.publisher.close.side_effect = RuntimeError('boom')

    with TestClient(build().initialize()):
        pass

    parts.connection.close.assert_awaited_once()
    parts.redis.close.assert_awaited_once()


def test_a_subscriber_that_failed_is_logged_and_shutdown_goes_on(parts):
    parts.subscriber.run = AsyncMock(side_effect=RuntimeError('bus is down'))

    with TestClient(build().initialize()):
        pass

    parts.connection.close.assert_awaited_once()


def test_health_is_unavailable_before_the_application_has_started(parts):
    # Without `with`, the lifespan has not run, so no subscriber is running
    response = TestClient(build().initialize()).get('/signal/health')

    assert response.status_code == 503
    assert response.json()['reason'] == 'the signal subscriber is not running'


def test_health_is_unavailable_when_the_subscriber_has_stopped(parts):
    parts.subscriber.run = AsyncMock(side_effect=RuntimeError('bus is down'))

    with TestClient(build().initialize()) as client:
        response = client.get('/signal/health')

    assert response.status_code == 503
    assert response.json()['reason'] == 'the signal subscriber is not running'


def test_health_checks_the_database_when_there_is_one(parts):
    session = MagicMock()
    session.execute = AsyncMock()
    database = MagicMock()
    database.dispose = AsyncMock()
    database.session.return_value.__aenter__ = AsyncMock(return_value=session)
    database.session.return_value.__aexit__ = AsyncMock(return_value=False)

    with TestClient(build(database=database).initialize()) as client:
        response = client.get('/signal/health')

    assert response.json()['status'] == 'ok'
    session.execute.assert_awaited_once()


def test_health_is_unavailable_when_the_database_does_not_answer(parts):
    session = MagicMock()
    session.execute = AsyncMock(side_effect=RuntimeError('no database'))
    database = MagicMock()
    database.dispose = AsyncMock()
    database.session.return_value.__aenter__ = AsyncMock(return_value=session)
    database.session.return_value.__aexit__ = AsyncMock(return_value=False)

    with TestClient(build(database=database).initialize()) as client:
        response = client.get('/signal/health')

    assert response.status_code == 503
    assert response.json()['reason'] == 'the database is not reachable'


def test_a_subscription_and_its_handler_go_together():
    with pytest.raises(ValueError):
        ServiceApplication(name='X', routers=[], subscription=CoreRecipeSignalSubscription())

    with pytest.raises(ValueError):
        ServiceApplication(name='X', routers=[], handler=handler)


def test_a_service_without_a_bus_gets_redis_and_the_index_route_only(parts):
    application = ServiceApplication(name='Session', routers=[]).initialize()

    with TestClient(application) as client:
        assert client.get('/').json() == {}
        assert client.get('/signal/health').status_code == 404
        assert application.state.redis is parts.redis
        assert application.state.token_verifier is parts.verifier
        assert not hasattr(application.state, 'service_bus')

    parts.redis.close.assert_awaited_once()
    parts.connection.close.assert_not_awaited()
    parts.subscriber.run.assert_not_awaited()


def test_the_startup_hook_runs_once_the_shared_parts_are_open_and_the_shutdown_hook_before_they_close(parts):
    order = []

    async def startup(application):
        order.append(('startup', application.state.redis, hasattr(application.state, 'signal_task')))

    async def shutdown(application):
        order.append(('shutdown', parts.redis.close.await_count, parts.stopped.is_set()))

    with TestClient(build(startup=startup, shutdown=shutdown).initialize()):
        pass

    assert order == [('startup', parts.redis, True), ('shutdown', 0, True)]


def test_the_hooks_work_without_a_bus_too(parts):
    seen = []

    async def startup(application):
        application.state.thing = 'ready'
        seen.append('startup')

    async def shutdown(application):
        seen.append(application.state.thing)

    application = ServiceApplication(name='Session', routers=[], startup=startup, shutdown=shutdown).initialize()

    with TestClient(application):
        pass

    assert seen == ['startup', 'ready']


def test_a_shutdown_hook_that_fails_does_not_stop_the_rest(parts):
    async def shutdown(application):
        raise RuntimeError('boom')

    with TestClient(build(shutdown=shutdown).initialize()):
        pass

    parts.connection.close.assert_awaited_once()
    parts.redis.close.assert_awaited_once()


def test_a_request_that_fails_because_the_bus_is_down_is_answered_with_503(parts):
    from cynthus.messaging.publisher import SignalBusUnavailable

    router = APIRouter()

    @router.get('/needs-the-bus')
    async def needs_the_bus():
        raise SignalBusUnavailable('down')

    with TestClient(build(routers=[router]).initialize()) as client:
        response = client.get('/needs-the-bus')

    assert response.status_code == 503
    assert response.json()['code'] == 'service_unavailable'
    assert response.headers['retry-after']
