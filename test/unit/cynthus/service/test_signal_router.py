"""Tests for cynthus.service.signal_router (SignalRouter).

Handlers are plain async functions. Results that are events go through a registry built from a test-only generator
with local event, signal, payload and message classes, because the real generator cannot take a ``SignalEvent`` yet.
"""

import asyncio
import inspect
from typing import ClassVar
from uuid import uuid4

import pytest

from cynthus.core.event import EventAction, SignalEvent, UserEvent
from cynthus.core.resource import StorageLocation
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.message_base import SignalMessageBase
from cynthus.messaging.common.signal.payload import SignalPayload
from cynthus.messaging.generator.signal_contract import SignalContract
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.publisher.signal_publisher import SignalPublisher
from cynthus.messaging.registry import SignalGeneratorRegistry, UnknownEventError
from cynthus.messaging.subscriber.received_signal import ReceivedSignal
from cynthus.service import ServiceModule, SignalConsumer, SignalRouter, UnknownSignalError

NAME = 'public.partner.service.requested'
OTHER = 'public.partner.service.listed'
ANSWER = 'public.partner.service.answered'


class ProbeCreatedSignal(SignalBase):
    domain = SignalDomainType.INVENTORY
    aggregate = 'probe'
    action = SignalActionType.CREATED


class ProbeUpdatedSignal(SignalBase):
    domain = SignalDomainType.INVENTORY
    aggregate = 'probe'
    action = SignalActionType.UPDATED


class ProbePayload(SignalPayload):
    schema_version: int = 1
    note: str


class ProbeCreatedMessage(SignalMessageBase):
    event_type: str = ProbeCreatedSignal.name
    payload: ProbePayload


class ProbeUpdatedMessage(SignalMessageBase):
    event_type: str = ProbeUpdatedSignal.name
    payload: ProbePayload


class ProbeEvent(UserEvent):
    """A local event published through the registry"""


class ProbeSignalEvent(SignalEvent):
    """A local signal event published through the registry"""


class ProbeGenerator(SignalGenerator):
    contracts: ClassVar = (
        SignalContract(
            features=('FT-TEST-001',),
            event='ProbeEvent',
            signal=ProbeCreatedSignal,
            message=ProbeCreatedMessage,
            payload=ProbePayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='created',
            sources={'note': 'data.note'},
        ),
        SignalContract(
            features=('FT-TEST-001',),
            event='ProbeSignalEvent',
            signal=ProbeUpdatedSignal,
            message=ProbeUpdatedMessage,
            payload=ProbePayload,
            lifecycle_action=LifecycleAction.UPDATED,
            method='updated',
            sources={'note': 'data.note'},
        ),
    )

    def created(self, event):
        contract = self.contract('created')

        return contract.message(
            **self.envelope(event, contract), payload=ProbePayload(note=event.data['note'])
        )

    def updated(self, event):
        contract = self.contract('updated')

        return contract.message(
            event_id=event.id_,
            timestamp=event.occurred_on,
            tenant_id=event.tenant_id,
            workspace_id=event.workspace_id,
            correlation_id=event.correlation_id,
            actor_id=event.actor_id,
            lifecycle_action=contract.lifecycle_action,
            payload=ProbePayload(note=event.data['note']),
        )


class Recording(SignalPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, message, access_token=None, *, topic=None):
        self.calls.append((message, access_token, topic))


class Failing(SignalPublisher):
    async def publish(self, message, access_token=None, *, topic=None):
        raise ConnectionError('broker down')


class BaseError(Exception):
    pass


class SubError(BaseError):
    pass


class CustomBase(BaseException):
    pass


def make_message(note='ok', cls=ProbeCreatedMessage):
    return cls(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        tenant_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProbePayload(note=note),
    )


def make_probe_event(note='hello'):
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

    return ProbeEvent(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, user=user,
        action=EventAction.CREATED, data={'note': note},
    )


def make_probe_signal_event(note='hello'):
    return ProbeSignalEvent(
        tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=EventAction.UPDATED, data={'note': note}
    )


def received(name=NAME):
    return ReceivedSignal(event_type=name, body='{}')


@pytest.fixture
def registry():
    return SignalGeneratorRegistry([ProbeGenerator])


@pytest.fixture
def router(registry):
    return SignalRouter(registry)


@pytest.fixture
def publisher():
    return Recording()


def test_dispatch_is_a_coroutine_function_with_the_documented_parameters():
    assert inspect.iscoroutinefunction(SignalRouter.dispatch)
    assert list(inspect.signature(SignalRouter.dispatch).parameters) == ['self', 'signal', 'publisher']


def test_the_registry_is_optional():
    assert inspect.signature(SignalRouter).parameters['registry'].default is None


@pytest.mark.asyncio
class TestDispatchCallsTheFunction:
    async def test_it_is_called_once_with_the_same_signal_and_publisher_objects(self, router, publisher):
        calls = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            calls.append((signal, pub))

        signal = received()

        await router.dispatch(signal, publisher)

        assert len(calls) == 1
        assert calls[0][0] is signal
        assert calls[0][1] is publisher

    async def test_dispatch_returns_none(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            return make_message()

        assert await router.dispatch(received(), publisher) is None

    async def test_the_function_of_the_signal_name_runs_and_no_other(self, router, publisher):
        ran = []

        @router.subscriber(NAME)
        async def first(signal, pub):
            ran.append('first')

        @router.subscriber(OTHER)
        async def second(signal, pub):
            ran.append('second')

        await router.dispatch(received(OTHER), publisher)

        assert ran == ['second']

    async def test_an_unknown_signal_raises_and_calls_nothing(self, router, publisher):
        ran = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            ran.append(signal)

        with pytest.raises(UnknownSignalError):
            await router.dispatch(received(OTHER), publisher)

        assert ran == [] and publisher.calls == []

    async def test_the_unknown_signal_error_names_the_signal(self, router, publisher):
        with pytest.raises(UnknownSignalError) as caught:
            await router.dispatch(received(OTHER), publisher)

        assert OTHER in str(caught.value)

    async def test_a_router_with_no_functions_raises_for_any_signal(self, router, publisher):
        with pytest.raises(UnknownSignalError):
            await router.dispatch(received(), publisher)

    async def test_an_unknown_signal_is_not_handled_by_an_exception_handler(self, router, publisher):
        @router.exception_handler(Exception)
        async def catch_all(error, signal):
            return make_message()

        with pytest.raises(UnknownSignalError):
            await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_two_routers_do_not_share_functions(self, registry, publisher):
        one, two = SignalRouter(registry), SignalRouter(registry)

        @one.subscriber(NAME)
        async def handle(signal, pub):
            pass

        with pytest.raises(UnknownSignalError):
            await two.dispatch(received(), publisher)


@pytest.mark.asyncio
class TestPublishingTheResult:
    async def test_a_message_is_published_as_is_once_with_no_token(self, router, publisher):
        message = make_message()

        @router.subscriber(NAME)
        async def handle(signal, pub):
            return message

        await router.dispatch(received(), publisher)

        assert len(publisher.calls) == 1
        published, token, topic = publisher.calls[0]

        assert published is message
        assert token is None
        assert topic is None

    async def test_the_token_of_the_received_signal_is_not_attached(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            return make_message()

        signal = ReceivedSignal(event_type=NAME, body='{}', properties={'authorization': 'Bearer abc'})

        await router.dispatch(signal, publisher)

        assert publisher.calls[0][1] is None

    async def test_none_publishes_nothing(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            return None

        await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_a_function_that_publishes_itself_and_returns_nothing_publishes_once(self, router, publisher):
        message = make_message()

        @router.subscriber(NAME)
        async def handle(signal, pub):
            await pub.publish(message)

        await router.dispatch(received(), publisher)

        assert [call[0] for call in publisher.calls] == [message]

    async def test_a_signal_event_is_published_through_the_registry_generator(self, router, publisher):
        event = make_probe_signal_event('from signal event')

        @router.subscriber(NAME)
        async def handle(signal, pub):
            return event

        await router.dispatch(received(), publisher)

        assert len(publisher.calls) == 1
        message, token, _ = publisher.calls[0]

        assert type(message) is ProbeUpdatedMessage
        assert message.event_type == ProbeUpdatedSignal.name
        assert message.payload.note == 'from signal event'
        assert message.correlation_id == event.correlation_id
        assert message.tenant_id == event.tenant_id
        assert token is None

    async def test_an_event_is_published_through_the_registry_generator(self, router, publisher):
        event = make_probe_event('from event')

        @router.subscriber(NAME)
        async def handle(signal, pub):
            return event

        await router.dispatch(received(), publisher)

        assert len(publisher.calls) == 1
        message, token, _ = publisher.calls[0]

        assert type(message) is ProbeCreatedMessage
        assert message.event_type == ProbeCreatedSignal.name
        assert message.payload.note == 'from event'
        assert message.correlation_id == event.correlation_id
        assert token is None

    async def test_an_event_without_a_generator_raises_and_publishes_nothing(self, publisher):
        router = SignalRouter(SignalGeneratorRegistry())

        @router.subscriber(NAME)
        async def handle(signal, pub):
            return make_probe_event()

        with pytest.raises(UnknownEventError):
            await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_the_default_registry_is_used_when_none_is_given(self, publisher):
        from cynthus.core.event import InventoryShelfCreatedEvent
        from cynthus.messaging.component.inventory.message import InventoryShelfCreatedMessage

        router = SignalRouter()
        probe = make_probe_event()
        event = InventoryShelfCreatedEvent(
            name='E0002', tenant=probe.tenant, workspace=probe.workspace, resource=probe.resource, user=probe.user,
            action=EventAction.CREATED,
            data={'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf', 'position': 4},
        )

        @router.subscriber(NAME)
        async def handle(signal, pub):
            return event

        await router.dispatch(received(), publisher)

        assert type(publisher.calls[0][0]) is InventoryShelfCreatedMessage

    @pytest.mark.parametrize('result', ['text', 42, 1.5, True, {'a': 1}, [make_message()], (make_message(),), object()])
    async def test_any_other_result_raises_type_error_and_publishes_nothing(self, router, publisher, result):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            return result

        with pytest.raises(TypeError):
            await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_a_publish_error_propagates_unchanged(self, router):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            return make_message()

        with pytest.raises(ConnectionError, match='broker down'):
            await router.dispatch(received(), Failing())

    async def test_a_publish_error_is_not_given_to_the_exception_handlers(self, router):
        seen = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            return make_message()

        @router.exception_handler(Exception)
        async def catch_all(error, signal):
            seen.append(error)

        with pytest.raises(ConnectionError):
            await router.dispatch(received(), Failing())

        assert seen == []

    async def test_an_event_publish_error_propagates(self, router):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            return make_probe_signal_event()

        with pytest.raises(ConnectionError):
            await router.dispatch(received(), Failing())


@pytest.mark.asyncio
class TestExceptionHandlers:
    async def test_a_registered_exception_gives_the_handler_result_published(self, router, publisher):
        answer = make_message('failed')
        seen = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('boom')

        @router.exception_handler(BaseError)
        async def on_error(error, signal):
            seen.append((error, signal))

            return answer

        signal = received()

        await router.dispatch(signal, publisher)

        assert len(seen) == 1
        assert isinstance(seen[0][0], BaseError) and str(seen[0][0]) == 'boom'
        assert seen[0][1] is signal
        assert [call[0] for call in publisher.calls] == [answer]
        assert publisher.calls[0][1] is None

    async def test_the_handler_result_may_be_an_event(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('boom')

        @router.exception_handler(BaseError)
        async def on_error(error, signal):
            return make_probe_signal_event('handled')

        await router.dispatch(received(), publisher)

        assert type(publisher.calls[0][0]) is ProbeUpdatedMessage
        assert publisher.calls[0][0].payload.note == 'handled'

    async def test_a_handler_result_of_none_publishes_nothing(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('boom')

        @router.exception_handler(BaseError)
        async def on_error(error, signal):
            return None

        await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_a_handler_result_of_another_type_raises_type_error(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('boom')

        @router.exception_handler(BaseError)
        async def on_error(error, signal):
            return 'nope'

        with pytest.raises(TypeError):
            await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_a_subclass_exception_is_handled_by_the_handler_of_its_base(self, router, publisher):
        answer = make_message('base')

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise SubError('sub')

        @router.exception_handler(BaseError)
        async def on_base(error, signal):
            return answer

        await router.dispatch(received(), publisher)

        assert [call[0] for call in publisher.calls] == [answer]

    async def test_the_nearest_class_wins_whatever_the_registration_order(self, publisher):
        for base_first in (True, False):
            router = SignalRouter()
            sub_answer, base_answer = make_message('sub'), make_message('base')

            @router.subscriber(NAME)
            async def handle(signal, pub):
                raise SubError('sub')

            async def on_sub(error, signal):
                return sub_answer

            async def on_base(error, signal):
                return base_answer

            if base_first:
                router.exception_handler(BaseError)(on_base)
                router.exception_handler(SubError)(on_sub)
            else:
                router.exception_handler(SubError)(on_sub)
                router.exception_handler(BaseError)(on_base)

            recording = Recording()

            await router.dispatch(received(), recording)

            assert [call[0] for call in recording.calls] == [sub_answer]

    async def test_a_handler_for_exception_is_the_fallback_but_a_nearer_one_wins(self, router, publisher):
        near, far = make_message('near'), make_message('far')

        @router.subscriber(NAME)
        async def raises_value(signal, pub):
            raise ValueError('v')

        @router.subscriber(OTHER)
        async def raises_key(signal, pub):
            raise KeyError('k')

        @router.exception_handler(Exception)
        async def on_exception(error, signal):
            return far

        @router.exception_handler(ValueError)
        async def on_value(error, signal):
            return near

        await router.dispatch(received(NAME), publisher)
        await router.dispatch(received(OTHER), publisher)

        assert [call[0] for call in publisher.calls] == [near, far]

    async def test_an_unregistered_exception_propagates_unchanged_and_nothing_is_published(self, router, publisher):
        error = KeyError('unhandled')

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise error

        @router.exception_handler(BaseError)
        async def on_error(error_, signal):
            return make_message()

        with pytest.raises(KeyError) as caught:
            await router.dispatch(received(), publisher)

        assert caught.value is error
        assert publisher.calls == []

    async def test_with_no_handlers_at_all_the_exception_propagates_unchanged(self, router, publisher):
        error = RuntimeError('plain')

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise error

        with pytest.raises(RuntimeError) as caught:
            await router.dispatch(received(), publisher)

        assert caught.value is error

    async def test_a_base_exception_does_not_use_the_handler_of_a_subclass(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('base')

        @router.exception_handler(SubError)
        async def on_sub(error, signal):
            return make_message()

        with pytest.raises(BaseError):
            await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_an_exception_raised_by_the_handler_propagates(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('first')

        @router.exception_handler(BaseError)
        async def on_error(error, signal):
            raise LookupError('second')

        with pytest.raises(LookupError, match='second'):
            await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_the_handler_is_not_run_for_a_function_that_succeeds(self, router, publisher):
        seen = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            return None

        @router.exception_handler(Exception)
        async def on_error(error, signal):
            seen.append(error)

        await router.dispatch(received(), publisher)

        assert seen == []

    async def test_handlers_are_one_pass_a_handler_error_is_not_handled_again(self, router, publisher):
        seen = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('first')

        @router.exception_handler(BaseError)
        async def on_base(error, signal):
            seen.append('base')
            raise SubError('second')

        @router.exception_handler(SubError)
        async def on_sub(error, signal):
            seen.append('sub')

        with pytest.raises(SubError):
            await router.dispatch(received(), publisher)

        assert seen == ['base']


@pytest.mark.asyncio
class TestCancellationAndBaseExceptions:
    async def test_cancelled_error_propagates_even_with_a_handler_for_exception(self, router, publisher):
        seen = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise asyncio.CancelledError

        @router.exception_handler(Exception)
        async def catch_all(error, signal):
            seen.append(error)

            return make_message()

        with pytest.raises(asyncio.CancelledError):
            await router.dispatch(received(), publisher)

        assert seen == [] and publisher.calls == []

    async def test_cancelled_error_propagates_with_no_handler(self, router, publisher):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise asyncio.CancelledError

        with pytest.raises(asyncio.CancelledError):
            await router.dispatch(received(), publisher)

        assert publisher.calls == []

    async def test_another_base_exception_is_never_handled(self, router, publisher):
        seen = []

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise CustomBase('stop')

        @router.exception_handler(Exception)
        async def catch_all(error, signal):
            seen.append(error)

        with pytest.raises(CustomBase):
            await router.dispatch(received(), publisher)

        assert seen == [] and publisher.calls == []

    async def test_a_task_cancelled_while_the_function_waits_is_cancelled(self, router, publisher):
        started = asyncio.Event()

        @router.subscriber(NAME)
        async def handle(signal, pub):
            started.set()
            await asyncio.sleep(10)

        @router.exception_handler(Exception)
        async def catch_all(error, signal):
            return make_message()

        task = asyncio.ensure_future(router.dispatch(received(), publisher))

        await started.wait()
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        assert publisher.calls == []


class TestSubscriberRegistration:
    def test_it_returns_the_function_unchanged(self, router):
        async def handle(signal, pub):
            pass

        assert router.subscriber(NAME)(handle) is handle

    def test_the_decorator_form_leaves_the_function_callable(self, router):
        @router.subscriber(NAME)
        async def handle(signal, pub):
            return 'direct'

        assert inspect.iscoroutinefunction(handle)
        assert handle.__name__ == 'handle'

    @pytest.mark.parametrize(
        'name',
        ['', 'bad', 'a.b.c', 'a.b.c.d.e', 'Public.a.b.c', 'public.Inventory.shelf.created', 'public.a1.b.c',
         'public..shelf.created', 'public.a.b.c ', ' public.a.b.c', 'public.a-b.c.d', 'a.b.c.d\n', 'a.b.c.d '],
    )
    def test_a_name_that_is_not_a_signal_name_raises_value_error(self, router, name):
        async def handle(signal, pub):
            pass

        with pytest.raises(ValueError):
            router.subscriber(name)(handle)

    @pytest.mark.parametrize('name', ['public.partner.service.requested', 'a.b.c.d', 'a.b_c.d_e.f_g_h'])
    def test_a_valid_name_is_accepted(self, router, name):
        async def handle(signal, pub):
            pass

        assert router.subscriber(name)(handle) is handle

    def test_a_name_registered_twice_raises_value_error(self, router):
        async def first(signal, pub):
            pass

        async def second(signal, pub):
            pass

        router.subscriber(NAME)(first)

        with pytest.raises(ValueError):
            router.subscriber(NAME)(second)

    @pytest.mark.asyncio
    async def test_a_duplicate_does_not_replace_the_first_function(self, router, publisher):
        ran = []

        async def first(signal, pub):
            ran.append('first')

        async def second(signal, pub):
            ran.append('second')

        router.subscriber(NAME)(first)

        with pytest.raises(ValueError):
            router.subscriber(NAME)(second)

        await router.dispatch(received(), publisher)

        assert ran == ['first']

    @pytest.mark.asyncio
    async def test_two_decorators_for_one_name_do_not_replace_each_other(self, router, publisher):
        ran = []

        async def f(signal, pub):
            ran.append('f')

        async def g(signal, pub):
            ran.append('g')

        a = router.subscriber(NAME)
        b = router.subscriber(NAME)

        a(f)

        with pytest.raises(ValueError):
            b(g)

        await router.dispatch(received(), publisher)

        assert ran == ['f']

    def test_the_same_name_may_be_registered_on_two_routers(self, registry):
        async def handle(signal, pub):
            pass

        SignalRouter(registry).subscriber(NAME)(handle)
        SignalRouter(registry).subscriber(NAME)(handle)

    def test_a_sync_function_raises_type_error(self, router):
        def handle(signal, pub):
            pass

        with pytest.raises(TypeError):
            router.subscriber(NAME)(handle)

    def test_a_lambda_raises_type_error(self, router):
        with pytest.raises(TypeError):
            router.subscriber(NAME)(lambda signal, pub: None)

    def test_a_refused_function_does_not_take_the_name(self, router):
        def sync(signal, pub):
            pass

        async def handle(signal, pub):
            pass

        with pytest.raises(TypeError):
            router.subscriber(NAME)(sync)

        assert router.subscriber(NAME)(handle) is handle


class TestExceptionHandlerRegistration:
    def test_it_returns_the_function_unchanged(self, router):
        async def on_error(error, signal):
            pass

        assert router.exception_handler(BaseError)(on_error) is on_error

    def test_exception_itself_is_allowed(self, router):
        async def on_error(error, signal):
            pass

        assert router.exception_handler(Exception)(on_error) is on_error

    def test_a_sync_function_raises_type_error(self, router):
        def on_error(error, signal):
            pass

        with pytest.raises(TypeError):
            router.exception_handler(BaseError)(on_error)

    @pytest.mark.parametrize('kind', [int, str, object, BaseException, KeyboardInterrupt, asyncio.CancelledError])
    def test_a_type_that_is_not_an_exception_subclass_raises_type_error(self, router, kind):
        async def on_error(error, signal):
            pass

        with pytest.raises(TypeError):
            router.exception_handler(kind)(on_error)

    def test_a_type_registered_twice_raises_value_error(self, router):
        async def first(error, signal):
            pass

        async def second(error, signal):
            pass

        router.exception_handler(BaseError)(first)

        with pytest.raises(ValueError):
            router.exception_handler(BaseError)(second)

    @pytest.mark.asyncio
    async def test_two_decorators_for_one_type_do_not_replace_each_other(self, router, publisher):
        first_answer = make_message('first')

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('boom')

        async def f(error, signal):
            return first_answer

        async def g(error, signal):
            return make_message('second')

        a = router.exception_handler(BaseError)
        b = router.exception_handler(BaseError)

        a(f)

        with pytest.raises(ValueError):
            b(g)

        await router.dispatch(received(), publisher)

        assert [call[0] for call in publisher.calls] == [first_answer]

    def test_different_types_may_be_registered(self, router):
        async def on_error(error, signal):
            pass

        router.exception_handler(BaseError)(on_error)
        router.exception_handler(SubError)(on_error)

    @pytest.mark.asyncio
    async def test_a_duplicate_does_not_replace_the_first_handler(self, router, publisher):
        first_answer = make_message('first')

        @router.subscriber(NAME)
        async def handle(signal, pub):
            raise BaseError('boom')

        async def first(error, signal):
            return first_answer

        async def second(error, signal):
            return make_message('second')

        router.exception_handler(BaseError)(first)

        with pytest.raises(ValueError):
            router.exception_handler(BaseError)(second)

        await router.dispatch(received(), publisher)

        assert [call[0] for call in publisher.calls] == [first_answer]


class FakeMessage:
    def __init__(self, event_type):
        self.event_type = event_type
        self.message_id = event_type


class FakeReceiver:
    def __init__(self, messages):
        self._messages = list(messages)
        self.completed = []
        self.dead_lettered = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._messages:
            raise StopAsyncIteration

        return self._messages.pop(0)

    async def complete_message(self, message):
        self.completed.append(message)

    async def dead_letter_message(self, message, *, reason=None):
        self.dead_lettered.append((message, reason))


@pytest.mark.asyncio
class TestFeatureIntegration:
    """AC5f: the router is the handler of a ServiceModule and SignalConsumer settles each message by what it did"""

    async def test_the_module_accepts_the_router_as_its_handler(self, router):
        module = ServiceModule(name='partner', subscription='partner-sub', handler=router.dispatch)

        assert module.handler == router.dispatch
        assert module.subscription == 'partner-sub'

    async def test_handled_signals_complete_and_failing_or_unknown_ones_are_dead_lettered(self, router, publisher):
        from unittest.mock import MagicMock

        answer = make_message('answered')

        ran = []

        @router.subscriber(NAME)
        async def handled(signal, pub):
            ran.append('handled')

            return answer

        @router.subscriber(OTHER)
        async def failing(signal, pub):
            ran.append('failing')

            raise RuntimeError('function failed')

        module = ServiceModule(name='partner', subscription='partner-sub', handler=router.dispatch)
        receiver = FakeReceiver([FakeMessage(NAME), FakeMessage(OTHER), FakeMessage(ANSWER)])
        client = MagicMock()
        client.get_subscription_receiver = MagicMock(return_value=receiver)

        async def handler(message):
            # What ServiceApplication does: build the ReceivedSignal and call the module handler with the publisher
            await module.handler(received(message.event_type), publisher)

        await SignalConsumer(client, module.subscription, handler).run()

        assert [m.event_type for m in receiver.completed] == [NAME]
        assert [(m.event_type, reason) for m, reason in receiver.dead_lettered] == [
            (OTHER, 'processing_failed'),
            (ANSWER, 'processing_failed'),
        ]
        assert [call[0] for call in publisher.calls] == [answer]
        assert ran == ['handled', 'failing']

    async def test_a_handled_exception_completes_the_message_and_publishes_the_answer(self, router, publisher):
        from unittest.mock import MagicMock

        answer = make_message('error answer')

        @router.subscriber(NAME)
        async def failing(signal, pub):
            raise BaseError('handled')

        @router.exception_handler(BaseError)
        async def on_error(error, signal):
            return answer

        receiver = FakeReceiver([FakeMessage(NAME)])
        client = MagicMock()
        client.get_subscription_receiver = MagicMock(return_value=receiver)

        async def handler(message):
            await router.dispatch(received(message.event_type), publisher)

        await SignalConsumer(client, 'sub', handler).run()

        assert [m.event_type for m in receiver.completed] == [NAME]
        assert receiver.dead_lettered == []
        assert [call[0] for call in publisher.calls] == [answer]
