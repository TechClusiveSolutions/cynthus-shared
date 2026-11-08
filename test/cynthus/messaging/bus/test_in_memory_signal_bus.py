"""Tests for cynthus.messaging.bus.in_memory_signal_bus (InMemorySignalBus)."""

from uuid import uuid4

import pytest

from cynthus.messaging.bus.in_memory_signal_bus import InMemorySignalBus
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.message_base import SignalMessageBase
from cynthus.messaging.publisher.signal_publisher import SignalPublisher
from cynthus.messaging.subscriber.signal_subscriber import SignalSubscriber
from cynthus.messaging.topic.core_signal_topic import CoreSignalTopic
from cynthus.messaging.topic.signal_topic import SignalTopic


class OtherTopic(SignalTopic):
    name: str = 'other-topic'


def make_message(event_type='public.test.thing.created'):
    return SignalMessageBase(event_type=event_type, lifecycle_action=LifecycleAction.CREATED, correlation_id=uuid4(),
                             organization_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4())


def recorder(sink, name=None):
    async def handler(body):
        sink.append(name if name else body)

    return handler


def test_implements_both_interfaces():
    bus = InMemorySignalBus()

    assert isinstance(bus, SignalPublisher)
    assert isinstance(bus, SignalSubscriber)


@pytest.mark.asyncio
async def test_records_what_was_published_in_order():
    bus, first, second = InMemorySignalBus(), make_message('a.b.c.created'), make_message('a.b.c.updated')

    await bus.publish(first, topic=CoreSignalTopic())
    await bus.publish(second, topic=OtherTopic())

    assert [(signal.topic_name, signal.message) for signal in bus.published] == [
        ('cynthus-events-topic', first), ('other-topic', second)]


@pytest.mark.asyncio
async def test_published_to_filters_by_topic():
    bus, message, other = InMemorySignalBus(), make_message(), make_message()

    await bus.publish(message, topic=CoreSignalTopic())
    await bus.publish(other, topic=OtherTopic())

    assert bus.published_to(CoreSignalTopic()) == [message]
    assert bus.published_to(OtherTopic()) == [other]


@pytest.mark.asyncio
async def test_delivers_the_json_body_to_subscribers_of_the_topic():
    bus, received, message = InMemorySignalBus(), [], make_message()

    bus.subscribe(CoreSignalTopic(), 'cynthus-sub-core-api', recorder(received))
    await bus.publish(message, topic=CoreSignalTopic())

    assert received == [message.model_dump(mode='json')]
    assert received[0]['event_type'] == 'public.test.thing.created'
    assert received[0]['workspace_id'] == str(message.workspace_id)


@pytest.mark.asyncio
async def test_does_not_deliver_signals_from_other_topics():
    bus, received = InMemorySignalBus(), []

    bus.subscribe(CoreSignalTopic(), 'sub', recorder(received))
    await bus.publish(make_message(), topic=OtherTopic())

    assert received == []


@pytest.mark.asyncio
async def test_every_subscription_receives_the_signal_in_subscription_order():
    bus, calls = InMemorySignalBus(), []

    bus.subscribe(CoreSignalTopic(), 'first', recorder(calls, 'first'))
    bus.subscribe(CoreSignalTopic(), 'second', recorder(calls, 'second'))
    await bus.publish(make_message(), topic=CoreSignalTopic())

    assert calls == ['first', 'second']


@pytest.mark.asyncio
async def test_a_failing_handler_does_not_stop_the_others_or_the_publisher():
    bus, calls = InMemorySignalBus(), []

    async def broken(body):
        raise RuntimeError('boom')

    bus.subscribe(CoreSignalTopic(), 'broken', broken)
    bus.subscribe(CoreSignalTopic(), 'healthy', recorder(calls, 'healthy'))
    await bus.publish(make_message(), topic=CoreSignalTopic())

    assert calls == ['healthy']
    assert [(name, str(error)) for name, error in bus.failures] == [('broken', 'boom')]


@pytest.mark.asyncio
async def test_a_message_is_recorded_even_when_nobody_subscribes():
    bus = InMemorySignalBus()

    await bus.publish(make_message(), topic=CoreSignalTopic())

    assert len(bus.published) == 1
    assert bus.failures == []


@pytest.mark.asyncio
async def test_publishes_to_the_core_topic_when_no_topic_is_given_and_keeps_the_access_token():
    bus, message = InMemorySignalBus(), make_message()

    await bus.publish(message, 'abc.def.ghi')

    assert bus.published_to(CoreSignalTopic()) == [message]
    assert bus.published[0].access_token == 'abc.def.ghi'
