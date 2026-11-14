"""Tests for cynthus.messaging.publisher.event_message_publisher (EventMessagePublisher)."""

import dataclasses
import inspect

import pytest

from cynthus.core.event import InventoryEvent, InventoryShelfCreatedEvent
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.message_base import SignalMessageBase
from cynthus.messaging.component.inventory.generator import InventoryShelfSignalGenerator
from cynthus.messaging.component.inventory.message import InventoryShelfCreatedMessage
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.publisher.event_message_publisher import EventMessagePublisher
from cynthus.messaging.publisher.signal_publisher import SignalPublisher
from cynthus.messaging.registry import SignalGeneratorRegistry, UnknownEventError
from cynthus.messaging.topic.signal_topic import SignalTopic

_DATA = {'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf', 'position': 4}


class Boom(RuntimeError):
    """Raised by the failing generator below"""


class Recording(SignalPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, message, access_token=None, *, topic=None):
        self.calls.append((message, access_token, topic))


class Failing(SignalPublisher):
    async def publish(self, message, access_token=None, *, topic=None):
        raise ConnectionError('broker down')


class FailingGenerator(SignalGenerator):
    """Looks up fine for a shelf event but cannot build the message"""

    contracts = (dataclasses.replace(InventoryShelfSignalGenerator.contracts[0], method='created'),)

    def created(self, event):
        raise Boom('cannot build')


@pytest.fixture
def event(make_event):
    return make_event(InventoryShelfCreatedEvent, dict(_DATA))


def test_is_not_a_signal_publisher_subclass_but_wraps_one():
    assert not issubclass(EventMessagePublisher, SignalPublisher)
    assert inspect.iscoroutinefunction(EventMessagePublisher.publish)


def test_signal_publisher_is_unchanged():
    assert SignalPublisher.__abstractmethods__ == frozenset({'publish'})
    assert not hasattr(SignalPublisher, 'publish_event')
    assert list(inspect.signature(SignalPublisher.publish).parameters) == ['self', 'message', 'access_token', 'topic']


def test_publish_signature():
    parameters = inspect.signature(EventMessagePublisher.publish).parameters

    assert list(parameters) == ['self', 'event', 'access_token', 'topic']
    assert parameters['access_token'].default is None
    assert parameters['topic'].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters['topic'].default is None


@pytest.mark.asyncio
class TestPublish:
    async def test_one_transport_call_with_the_generated_message(self, event):
        transport = Recording()

        await EventMessagePublisher(transport).publish(event)

        assert len(transport.calls) == 1

        message = transport.calls[0][0]

        assert type(message) is InventoryShelfCreatedMessage
        assert message.event_type == 'public.inventory.shelf.created'
        assert message.lifecycle_action == LifecycleAction.CREATED
        assert message.tenant_id == event.tenant.id_
        assert message.workspace_id == event.workspace.id_
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.user.id_
        assert message.payload.shelf_id == 'shelf-1'
        assert message.payload.location_id == 'loc-1'
        assert message.payload.name == 'Top shelf'
        assert message.payload.position == 4

    async def test_returns_the_published_message(self, event):
        transport = Recording()

        returned = await EventMessagePublisher(transport).publish(event)

        assert returned is transport.calls[0][0]
        assert isinstance(returned, SignalMessageBase)
        assert returned.event_type == 'public.inventory.shelf.created'

    async def test_returned_message_is_not_the_event(self, event):
        returned = await EventMessagePublisher(Recording()).publish(event)

        assert returned is not event
        assert returned.event_type != event.event_type

    async def test_token_and_topic_pass_through(self, event):
        transport, topic = Recording(), SignalTopic(name='other-topic')

        await EventMessagePublisher(transport).publish(event, 'tok-123', topic=topic)

        _, token, passed = transport.calls[0]

        assert token == 'tok-123'
        assert passed is topic

    async def test_defaults_pass_none(self, event):
        transport = Recording()

        await EventMessagePublisher(transport).publish(event)

        assert transport.calls[0][1] is None
        assert transport.calls[0][2] is None

    async def test_none_registry_means_the_default_registry(self, event):
        transport = Recording()

        await EventMessagePublisher(transport, None).publish(event)

        assert len(transport.calls) == 1

    async def test_explicit_registry_is_used(self, event):
        transport = Recording()
        registry = SignalGeneratorRegistry([InventoryShelfSignalGenerator])

        await EventMessagePublisher(transport, registry=registry).publish(event)

        assert len(transport.calls) == 1

    async def test_empty_registry_is_honoured(self, event):
        transport = Recording()
        publisher = EventMessagePublisher(transport, SignalGeneratorRegistry([]))

        with pytest.raises(UnknownEventError):
            await publisher.publish(event)

        assert transport.calls == []

    async def test_unknown_event_never_calls_the_transport(self, make_event):
        transport = Recording()

        with pytest.raises(UnknownEventError, match='InventoryEvent'):
            await EventMessagePublisher(transport).publish(make_event(InventoryEvent, {}))

        assert transport.calls == []

    async def test_generation_failure_never_calls_the_transport(self, event):
        transport = Recording()
        publisher = EventMessagePublisher(transport, SignalGeneratorRegistry([FailingGenerator]))

        with pytest.raises(Boom, match='cannot build'):
            await publisher.publish(event)

        assert transport.calls == []

    async def test_transport_failure_propagates(self, event):
        with pytest.raises(ConnectionError, match='broker down'):
            await EventMessagePublisher(Failing()).publish(event)

    async def test_each_call_publishes_once(self, event):
        transport = Recording()
        publisher = EventMessagePublisher(transport)

        await publisher.publish(event)
        await publisher.publish(event)

        assert len(transport.calls) == 2
        assert transport.calls[0][0] == transport.calls[1][0]
