"""Tests for cynthus.service.service_application (ServiceApplication)."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from cynthus.messaging.subscriber import ReceivedSignal
from cynthus.messaging.subscription import CoreProfileSignalSubscription, CoreRecipeSignalSubscription
from cynthus.service import ServiceApplication, ServiceModule, ServiceOutage
from cynthus.service import service_application as module


class Parts:
    """Everything the application would open, replaced by fakes."""

    def __init__(self):
        self.redis = MagicMock()
        self.redis.close = AsyncMock()

        self.client = MagicMock()
        self.publisher = MagicMock()

        self.verifier = MagicMock()

        self.stopped = asyncio.Event()
        self.subscriber = MagicMock()
        self.subscriber.run = AsyncMock(side_effect=self._forever)

        self.broker = MagicMock(publisher=self.publisher, subscriber=self.subscriber, client=self.client)
        self.broker.close = AsyncMock()

    async def _forever(self):
        try:
            await asyncio.Event().wait()
        finally:
            self.stopped.set()


@pytest.fixture
def parts():
    fakes = Parts()

    with patch.object(module.RedisClient, 'from_environment', return_value=fakes.redis), \
            patch.object(module.SignalBroker, 'from_environment', return_value=fakes.broker), \
            patch.object(module.TokenVerifier, 'from_environment', return_value=fakes.verifier):
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


def test_the_subscriber_listens_on_the_subscription_of_the_chosen_broker(parts):
    with TestClient(build().initialize()):
        pass

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
    parts.broker.close.assert_awaited_once()
    parts.redis.close.assert_awaited_once()
    database.dispose.assert_awaited_once()


def test_a_failure_while_closing_one_thing_does_not_stop_the_others(parts):
    parts.broker.close.side_effect = RuntimeError('boom')

    with TestClient(build().initialize()):
        pass

    parts.broker.close.assert_awaited_once()
    parts.redis.close.assert_awaited_once()


def test_a_subscriber_that_failed_is_logged_and_shutdown_goes_on(parts):
    parts.subscriber.run = AsyncMock(side_effect=RuntimeError('bus is down'))

    with TestClient(build().initialize()):
        pass

    parts.broker.close.assert_awaited_once()


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
    parts.broker.close.assert_not_awaited()
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

    parts.broker.close.assert_awaited_once()
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


def test_the_publisher_reports_an_unreachable_bus_through_the_outage_flag(parts):
    with TestClient(build().initialize()) as client:
        outage = client.app.state.outage

        assert parts.publisher.on_unavailable == outage.report
        assert isinstance(outage, ServiceOutage)


# Several modules in one application (ADR-008)

def database(answers=True):
    session = MagicMock()
    session.execute = AsyncMock() if answers else AsyncMock(side_effect=RuntimeError('no database'))
    fake = MagicMock()
    fake.dispose = AsyncMock()
    fake.session.return_value.__aenter__ = AsyncMock(return_value=session)
    fake.session.return_value.__aexit__ = AsyncMock(return_value=False)

    return fake


def make_module(name, subscription, **overrides):
    values = dict(name=name, subscription=subscription, handler=handler)
    values.update(overrides)

    return ServiceModule(**values)


def hosted(*modules):
    return ServiceApplication(name='Domain', modules=list(modules))


def thing_router(path):
    router = APIRouter()

    @router.get(path)
    async def thing():
        return {'path': path}

    return router


def test_every_module_is_subscribed_over_the_one_broker(parts):
    with TestClient(hosted(
        make_module('Recipe', CoreRecipeSignalSubscription()),
        make_module('Profile', CoreProfileSignalSubscription()),
    ).initialize()):
        pass

    names = [call.args[1] for call in parts.subscriber.subscribe.call_args_list]

    assert names == ['cynthus-sub-core-recipe', CoreProfileSignalSubscription().name]
    parts.subscriber.run.assert_awaited_once()
    parts.broker.close.assert_awaited_once()


def test_the_routers_of_every_module_are_mounted_and_the_index_exists_once(parts):
    application = hosted(
        make_module('Recipe', CoreRecipeSignalSubscription(), routers=[thing_router('/recipes')]),
        make_module('Profile', CoreProfileSignalSubscription(), routers=[thing_router('/profiles')]),
    ).initialize()

    with TestClient(application) as client:
        assert client.get('/recipes').json() == {'path': '/recipes'}
        assert client.get('/profiles').json() == {'path': '/profiles'}
        assert client.get('/').json() == {}


def test_the_access_decisions_of_every_module_are_recorded_as_signals(parts):
    first, second = SimpleNamespace(recorder=None), SimpleNamespace(recorder=None)

    with patch.object(module, 'SignalAccessRecorder') as recorder_class:
        with TestClient(hosted(
            make_module('Recipe', CoreRecipeSignalSubscription(), signal_access=first),
            make_module('Profile', CoreProfileSignalSubscription(), signal_access=second),
        ).initialize()):
            assert first.recorder is second.recorder is recorder_class.return_value


def test_the_health_lists_every_module(parts):
    application = hosted(
        make_module('Recipe', CoreRecipeSignalSubscription(), database=database()),
        make_module('Profile', CoreProfileSignalSubscription(), database=database()),
    ).initialize()

    with TestClient(application) as client:
        body = client.get('/signal/health').json()

    assert body['status'] == 'ok'
    assert sorted(body['modules']) == ['Profile', 'Recipe']
    assert body['modules']['Recipe'] == {
        'subscription': 'cynthus-sub-core-recipe', 'topic': 'cynthus-events-topic', 'status': 'ok'}


def test_one_module_whose_database_is_down_makes_the_container_unavailable_and_is_named(parts):
    application = hosted(
        make_module('Recipe', CoreRecipeSignalSubscription(), database=database()),
        make_module('Profile', CoreProfileSignalSubscription(), database=database(answers=False)),
    ).initialize()

    with TestClient(application) as client:
        response = client.get('/signal/health')

    assert response.status_code == 503
    assert response.json()['status'] == 'unavailable'
    assert response.json()['modules']['Recipe']['status'] == 'ok'
    assert response.json()['modules']['Profile']['reason'] == 'the database is not reachable'


def test_a_module_can_be_checked_on_its_own(parts):
    application = hosted(
        make_module('Recipe', CoreRecipeSignalSubscription(), database=database()),
        make_module('Profile', CoreProfileSignalSubscription(), database=database(answers=False)),
    ).initialize()

    with TestClient(application) as client:
        assert client.get('/signal/health/Recipe').json()['status'] == 'ok'
        assert client.get('/signal/health/Profile').status_code == 503
        assert client.get('/signal/health/Nobody').status_code == 404


def test_a_stopped_subscriber_makes_every_module_unavailable(parts):
    parts.subscriber.run = AsyncMock(side_effect=RuntimeError('bus is down'))

    with TestClient(hosted(
        make_module('Recipe', CoreRecipeSignalSubscription()),
        make_module('Profile', CoreProfileSignalSubscription()),
    ).initialize()) as client:
        body = client.get('/signal/health').json()

    assert {entry['reason'] for entry in body['modules'].values()} == {'the signal subscriber is not running'}


def test_a_module_without_a_bus_takes_no_part_in_the_health(parts):
    application = hosted(
        make_module('Recipe', CoreRecipeSignalSubscription()),
        ServiceModule(name='Static', routers=[thing_router('/static')]),
    ).initialize()

    with TestClient(application) as client:
        assert list(client.get('/signal/health').json()['modules']) == ['Recipe']
        assert client.get('/static').status_code == 200


def test_modules_without_any_bus_get_no_signal_routes(parts):
    application = hosted(ServiceModule(name='Static')).initialize()

    with TestClient(application) as client:
        assert client.get('/signal/health').status_code == 404

    parts.broker.close.assert_not_awaited()


def test_start_up_hooks_run_in_order_and_shutdown_hooks_in_reverse_and_every_database_closes(parts):
    order = []
    first_database, second_database = database(), database()

    def hook(label):
        async def run(application):
            order.append(label)

        return run

    application = hosted(
        make_module('Recipe', CoreRecipeSignalSubscription(), database=first_database,
                    startup=hook('start recipe'), shutdown=hook('stop recipe')),
        make_module('Profile', CoreProfileSignalSubscription(), database=second_database,
                    startup=hook('start profile'), shutdown=hook('stop profile')),
    ).initialize()

    with TestClient(application):
        pass

    assert order == ['start recipe', 'start profile', 'stop profile', 'stop recipe']
    first_database.dispose.assert_awaited_once()
    second_database.dispose.assert_awaited_once()


def test_each_module_handler_gets_its_own_signals(parts):
    seen = []

    async def recipe_handler(signal, publisher):
        seen.append('recipe')

    async def profile_handler(signal, publisher):
        seen.append('profile')

    with TestClient(hosted(
        make_module('Recipe', CoreRecipeSignalSubscription(), handler=recipe_handler),
        make_module('Profile', CoreProfileSignalSubscription(), handler=profile_handler),
    ).initialize()):
        registered = [call.args[2] for call in parts.subscriber.subscribe.call_args_list]

        for handle in reversed(registered):
            asyncio.run(handle(ReceivedSignal(event_type='a.b.c', body='{}')))

    assert seen == ['profile', 'recipe']


def test_modules_and_the_single_module_arguments_are_one_or_the_other():
    with pytest.raises(ValueError, match='either modules or'):
        ServiceApplication(name='X', routers=[APIRouter()], modules=[ServiceModule(name='A')])

    with pytest.raises(ValueError, match='either modules or'):
        ServiceApplication(name='X', handler=handler, subscription=CoreRecipeSignalSubscription(),
                           modules=[ServiceModule(name='A')])


def test_there_must_be_a_module_and_their_names_must_differ():
    with pytest.raises(ValueError, match='at least one'):
        ServiceApplication(name='X', modules=[])

    with pytest.raises(ValueError, match='different: A, A'):
        ServiceApplication(name='X', modules=[ServiceModule(name='A'), ServiceModule(name='A')])


def test_a_module_needs_its_subscription_and_handler_together():
    with pytest.raises(ValueError):
        ServiceModule(name='A', subscription=CoreRecipeSignalSubscription())


def test_a_handler_that_runs_too_long_is_cancelled_and_its_signal_dead_lettered(parts, monkeypatch):
    monkeypatch.setenv('SIGNAL_HANDLER_TIMEOUT_SECONDS', '0.05')
    cancelled = []

    async def slow(signal, publisher):
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            cancelled.append(True)
            raise

    with TestClient(build(handler=slow).initialize()):
        registered = parts.subscriber.subscribe.call_args.args[2]

        with pytest.raises(TimeoutError, match='Recipe handler did not finish within 0.05 seconds'):
            asyncio.run(registered(ReceivedSignal(event_type='a.b.c', body='{}')))

    assert cancelled == [True]


def test_zero_turns_the_handler_limit_off(parts, monkeypatch):
    monkeypatch.setenv('SIGNAL_HANDLER_TIMEOUT_SECONDS', '0')

    assert build()._handler_timeout is None


@pytest.mark.parametrize('value, expected', [('', 60.0), ('  ', 60.0), ('12', 12.0), (' 2.5 ', 2.5)])
def test_the_handler_limit_comes_from_the_environment(parts, monkeypatch, value, expected):
    monkeypatch.setenv('SIGNAL_HANDLER_TIMEOUT_SECONDS', value)

    assert build()._handler_timeout == expected


@pytest.mark.parametrize('value', ['soon', '-1'])
def test_a_bad_handler_limit_stops_the_service_and_names_the_setting(parts, monkeypatch, value):
    monkeypatch.setenv('SIGNAL_HANDLER_TIMEOUT_SECONDS', value)

    with pytest.raises(ValueError, match='SIGNAL_HANDLER_TIMEOUT_SECONDS must be a number of seconds'):
        build()
