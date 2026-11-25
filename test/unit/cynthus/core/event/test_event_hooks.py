"""EventHooks class unit tests for the Cynthus project"""

import asyncio
import logging
from uuid import uuid4

import pytest

from cynthus.core.event import Event, EventAction, EventHooks, SignalEvent
from cynthus.core.resource import StorageLocation
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User


class ThingHappenedEvent(SignalEvent):
    """Local SignalEvent subclass"""


class OtherThingEvent(SignalEvent):
    """Unrelated SignalEvent subclass"""


def _signal(cls=ThingHappenedEvent):
    return cls(
        tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=EventAction.RETRIEVED, data={}
    )


def _plain_event():
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

    return Event(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, action=EventAction.CREATED, data={}
    )


class _Recorder:
    """Collects the calls of hooks in order"""

    def __init__(self):
        self.calls = []

    def hook(self, label):
        async def _hook(event):
            self.calls.append((label, event))

        return _hook


class TestEventHooks:
    """Tests the EventHooks class"""

    @pytest.mark.asyncio
    async def test_hook_is_called_with_the_event_only(self):
        hooks, recorder, event = EventHooks(), _Recorder(), _signal()
        hooks.register(ThingHappenedEvent, recorder.hook('a'))

        await hooks.fire(event)

        assert recorder.calls == [('a', event)]
        assert recorder.calls[0][1] is event

    @pytest.mark.asyncio
    async def test_register_returns_none(self):
        assert EventHooks().register(ThingHappenedEvent, _Recorder().hook('a')) is None

    @pytest.mark.asyncio
    async def test_fire_returns_none(self):
        assert await EventHooks().fire(_signal()) is None

    @pytest.mark.asyncio
    async def test_hooks_run_in_registration_order(self):
        hooks, recorder = EventHooks(), _Recorder()
        for label in ('a', 'b', 'c'):
            hooks.register(ThingHappenedEvent, recorder.hook(label))

        await hooks.fire(_signal())

        assert [label for label, _ in recorder.calls] == ['a', 'b', 'c']

    @pytest.mark.asyncio
    async def test_hook_for_a_base_class_is_called(self):
        hooks, recorder = EventHooks(), _Recorder()
        hooks.register(SignalEvent, recorder.hook('base'))

        await hooks.fire(_signal())

        assert [label for label, _ in recorder.calls] == ['base']

    @pytest.mark.asyncio
    async def test_class_and_base_class_hooks_run_in_registration_order(self):
        hooks, recorder = EventHooks(), _Recorder()
        hooks.register(SignalEvent, recorder.hook('base'))
        hooks.register(ThingHappenedEvent, recorder.hook('own'))
        hooks.register(SignalEvent, recorder.hook('base2'))

        await hooks.fire(_signal())

        assert [label for label, _ in recorder.calls] == ['base', 'own', 'base2']

    @pytest.mark.asyncio
    async def test_hook_for_a_subclass_is_not_called_for_the_base(self):
        hooks, recorder = EventHooks(), _Recorder()
        hooks.register(ThingHappenedEvent, recorder.hook('sub'))

        await hooks.fire(_signal(SignalEvent))

        assert recorder.calls == []

    @pytest.mark.asyncio
    async def test_hook_for_an_unrelated_class_is_not_called(self):
        hooks, recorder = EventHooks(), _Recorder()
        hooks.register(OtherThingEvent, recorder.hook('other'))
        hooks.register(Event, recorder.hook('event'))

        await hooks.fire(_signal())

        assert recorder.calls == []

    @pytest.mark.asyncio
    async def test_no_hooks_does_nothing(self):
        await EventHooks().fire(_signal())
        await EventHooks().fire(_plain_event())

    @pytest.mark.asyncio
    async def test_plain_event_hooks_run(self):
        hooks, recorder, event = EventHooks(), _Recorder(), _plain_event()
        hooks.register(Event, recorder.hook('event'))
        hooks.register(SignalEvent, recorder.hook('signal'))

        await hooks.fire(event)

        assert recorder.calls == [('event', event)]

    @pytest.mark.asyncio
    async def test_signal_event_hook_for_event_is_not_called(self):
        hooks, recorder = EventHooks(), _Recorder()
        hooks.register(Event, recorder.hook('event'))

        await hooks.fire(_signal())

        assert recorder.calls == []

    @pytest.mark.asyncio
    async def test_each_instance_has_its_own_registry(self):
        first, second, recorder = EventHooks(), EventHooks(), _Recorder()
        first.register(ThingHappenedEvent, recorder.hook('first'))

        await second.fire(_signal())

        assert recorder.calls == []

    @pytest.mark.asyncio
    async def test_hook_is_awaited_before_the_next_one_starts(self):
        hooks, order = EventHooks(), []

        async def slow(event):
            order.append('slow start')
            await asyncio.sleep(0)
            order.append('slow end')

        async def fast(event):
            order.append('fast')

        hooks.register(ThingHappenedEvent, slow)
        hooks.register(ThingHappenedEvent, fast)

        await hooks.fire(_signal())

        assert order == ['slow start', 'slow end', 'fast']

    @pytest.mark.asyncio
    async def test_same_hook_can_be_fired_more_than_once(self):
        hooks, recorder = EventHooks(), _Recorder()
        hooks.register(ThingHappenedEvent, recorder.hook('a'))

        await hooks.fire(_signal())
        await hooks.fire(_signal())

        assert len(recorder.calls) == 2


class TestEventHooksFailures:
    """Tests failing and cancelled hooks"""

    @pytest.mark.asyncio
    async def test_raising_hook_is_logged_and_next_hook_runs(self, caplog):
        hooks, recorder = EventHooks(), _Recorder()

        async def failing(event):
            raise RuntimeError('hook broke')

        hooks.register(ThingHappenedEvent, recorder.hook('before'))
        hooks.register(ThingHappenedEvent, failing)
        hooks.register(ThingHappenedEvent, recorder.hook('after'))

        with caplog.at_level(logging.ERROR):
            await hooks.fire(_signal())

        assert [label for label, _ in recorder.calls] == ['before', 'after']
        errors = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert len(errors) == 1
        assert 'thing_happened' in errors[0].getMessage()

    @pytest.mark.asyncio
    async def test_raising_hook_for_plain_event_is_logged(self, caplog):
        hooks, recorder = EventHooks(), _Recorder()

        async def failing(event):
            raise ValueError('nope')

        hooks.register(Event, failing)
        hooks.register(Event, recorder.hook('after'))

        with caplog.at_level(logging.ERROR):
            await hooks.fire(_plain_event())

        assert len(recorder.calls) == 1
        assert any(r.levelno == logging.ERROR for r in caplog.records)

    @pytest.mark.asyncio
    async def test_fire_does_not_raise_when_every_hook_fails(self, caplog):
        hooks = EventHooks()

        async def failing(event):
            raise RuntimeError('boom')

        hooks.register(ThingHappenedEvent, failing)
        hooks.register(SignalEvent, failing)

        with caplog.at_level(logging.ERROR):
            await hooks.fire(_signal())

        assert len([r for r in caplog.records if r.levelno == logging.ERROR]) == 2

    @pytest.mark.asyncio
    async def test_successful_hooks_log_no_error(self, caplog):
        hooks = EventHooks()
        hooks.register(ThingHappenedEvent, _Recorder().hook('a'))

        with caplog.at_level(logging.ERROR):
            await hooks.fire(_signal())

        assert not [r for r in caplog.records if r.levelno >= logging.ERROR]

    @pytest.mark.asyncio
    async def test_cancelled_error_propagates_and_stops_later_hooks(self):
        hooks, recorder = EventHooks(), _Recorder()

        async def cancelling(event):
            raise asyncio.CancelledError()

        hooks.register(ThingHappenedEvent, cancelling)
        hooks.register(ThingHappenedEvent, recorder.hook('after'))

        with pytest.raises(asyncio.CancelledError):
            await hooks.fire(_signal())

        assert recorder.calls == []

    @pytest.mark.asyncio
    async def test_cancelled_error_is_not_logged_as_a_failure(self, caplog):
        hooks = EventHooks()

        async def cancelling(event):
            raise asyncio.CancelledError()

        hooks.register(Event, cancelling)

        with caplog.at_level(logging.ERROR), pytest.raises(asyncio.CancelledError):
            await hooks.fire(_plain_event())

        assert not [r for r in caplog.records if r.levelno >= logging.ERROR]


class TestEventHooksFeature:
    """Feature-style test: hooks fire for a SignalEvent subclass and a plain Event"""

    @pytest.mark.asyncio
    async def test_hooks_fire_for_signal_subclass_and_plain_event(self):
        hooks, recorder = EventHooks(), _Recorder()
        hooks.register(SignalEvent, recorder.hook('any signal'))
        hooks.register(ThingHappenedEvent, recorder.hook('thing'))
        hooks.register(OtherThingEvent, recorder.hook('other'))
        hooks.register(Event, recorder.hook('any event'))

        signal, plain = _signal(), _plain_event()
        await hooks.fire(signal)
        await hooks.fire(plain)

        assert recorder.calls == [
            ('any signal', signal),
            ('thing', signal),
            ('any event', plain),
        ]


class TestEventHooksRegisterDuringFire:
    """Tests registering a hook while fire is running"""

    @pytest.mark.asyncio
    async def test_hook_registered_during_fire_runs_on_the_next_fire_only(self):
        hooks, recorder = EventHooks(), _Recorder()

        async def registering(event):
            hooks.register(ThingHappenedEvent, recorder.hook('late'))

        hooks.register(ThingHappenedEvent, registering)

        await hooks.fire(_signal())
        assert recorder.calls == []

        await hooks.fire(_signal())
        assert [label for label, _ in recorder.calls] == ['late']
