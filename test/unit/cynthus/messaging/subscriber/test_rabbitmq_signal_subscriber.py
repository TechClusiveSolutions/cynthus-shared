"""Tests for cynthus.messaging.subscriber.rabbitmq_signal_subscriber (RabbitMqSignalSubscriber)."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from cynthus.messaging.rabbitmq import RabbitMqConnection
from cynthus.messaging.subscriber import RabbitMqSignalSubscriber, SignalSubscriber
from cynthus.messaging.topic import CoreSignalTopic

TOPIC = CoreSignalTopic()


def incoming(event_type='public.test.thing.created', **overrides):
    values = dict(
        type=event_type, routing_key=event_type, body=b'{"a": 1}', message_id='m-1', correlation_id='c-1',
        headers={'authorization': 'Bearer abc.def.ghi'},
    )
    values.update(overrides)
    message = SimpleNamespace(**values)
    message.ack = AsyncMock()
    message.reject = AsyncMock()

    return message


class Messages:
    """What ``queue.iterator()`` returns: an async context manager that yields the given messages and then ends."""

    def __init__(self, messages):
        self._messages = list(messages)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def __aiter__(self):
        return self._generate()

    async def _generate(self):
        for message in self._messages:
            yield message


def connection_for(fake, *messages):
    fake.queue.iterator = MagicMock(return_value=Messages(messages))
    connection = MagicMock(spec=RabbitMqConnection)
    connection.channel = AsyncMock(return_value=fake.channel)

    return connection


def test_it_is_a_signal_subscriber(fake_aio_pika):
    assert isinstance(RabbitMqSignalSubscriber(connection_for(fake_aio_pika)), SignalSubscriber)


@pytest.mark.asyncio
async def test_the_topology_is_declared_and_the_queue_is_bound_to_every_event(fake_aio_pika):
    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika))
    subscriber.subscribe(TOPIC, 'cynthus-profile-sub', AsyncMock())

    await subscriber.run()

    channel = fake_aio_pika.channel
    channel.set_qos.assert_awaited_once_with(prefetch_count=10)
    exchanges = [call.args for call in channel.declare_exchange.await_args_list]
    assert exchanges == [('cynthus-events-topic.dlx', 'direct'), ('cynthus-events-topic', 'topic')]

    queues = {call.args[0]: call.kwargs for call in channel.declare_queue.await_args_list}
    assert queues['cynthus-profile-sub.dlq']['arguments'] == {'x-queue-type': 'quorum'}
    assert queues['cynthus-profile-sub']['arguments']['x-delivery-limit'] == 10
    assert queues['cynthus-profile-sub']['arguments']['x-dead-letter-routing-key'] == 'cynthus-profile-sub'
    assert all(options['durable'] for options in queues.values())

    bound = [(call.args, call.kwargs) for call in fake_aio_pika.queue.bind.await_args_list]
    assert bound[0][1] == {'routing_key': 'cynthus-profile-sub'}
    assert bound[1][1] == {'routing_key': '#'}


@pytest.mark.asyncio
async def test_a_signal_the_handler_accepts_is_acknowledged_with_everything_the_handler_needs(fake_aio_pika):
    message = incoming()
    seen = []

    async def handler(signal):
        seen.append(signal)

    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika, message))
    subscriber.subscribe(TOPIC, 'sub', handler)

    await subscriber.run()

    message.ack.assert_awaited_once()
    message.reject.assert_not_awaited()
    assert seen[0].event_type == 'public.test.thing.created'
    assert seen[0].payload == {'a': 1}
    assert seen[0].access_token == 'abc.def.ghi'
    assert seen[0].correlation_id == 'c-1'


@pytest.mark.asyncio
async def test_a_signal_the_handler_raises_on_is_rejected_without_requeue_and_the_next_one_still_arrives(fake_aio_pika):
    bad, good = incoming(message_id='bad'), incoming(message_id='good')
    handled = []

    async def handler(signal):
        handled.append(signal.message_id)

        if signal.message_id == 'bad':
            raise RuntimeError('cannot handle')

    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika, bad, good))
    subscriber.subscribe(TOPIC, 'sub', handler)

    await subscriber.run()

    bad.reject.assert_awaited_once_with(requeue=False)
    bad.ack.assert_not_awaited()
    good.ack.assert_awaited_once()
    assert handled == ['bad', 'good']


@pytest.mark.asyncio
async def test_cancelling_leaves_the_signal_in_hand_unsettled_for_redelivery(fake_aio_pika):
    message = incoming()

    async def handler(signal):
        raise asyncio.CancelledError

    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika, message))
    subscriber.subscribe(TOPIC, 'sub', handler)

    with pytest.raises(asyncio.CancelledError):
        await subscriber.run()

    message.ack.assert_not_awaited()
    message.reject.assert_not_awaited()
    fake_aio_pika.channel.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_the_channel_is_closed_when_the_loop_ends(fake_aio_pika):
    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika))
    subscriber.subscribe(TOPIC, 'sub', AsyncMock())

    await subscriber.run()

    fake_aio_pika.channel.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_each_subscription_gets_its_own_channel_and_all_run_together(fake_aio_pika):
    connection = connection_for(fake_aio_pika, incoming())
    subscriber = RabbitMqSignalSubscriber(connection)
    first, second = AsyncMock(), AsyncMock()
    subscriber.subscribe(TOPIC, 'one', first)
    subscriber.subscribe(TOPIC, 'two', second)

    await subscriber.run()

    assert connection.channel.await_count == 2


@pytest.mark.asyncio
async def test_a_queue_that_exists_with_other_arguments_gets_an_explanation(fake_aio_pika):
    fake_aio_pika.channel.declare_queue.side_effect = RuntimeError('PRECONDITION_FAILED - inequivalent arg')
    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika))
    subscriber.subscribe(TOPIC, 'cynthus-profile-sub', AsyncMock())

    with pytest.raises(RuntimeError, match='cynthus-profile-sub already exists with different arguments'):
        await subscriber.run()

    fake_aio_pika.channel.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_any_other_declaration_error_is_not_disguised(fake_aio_pika):
    fake_aio_pika.channel.declare_queue.side_effect = OSError('connection reset')
    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika))
    subscriber.subscribe(TOPIC, 'sub', AsyncMock())

    with pytest.raises(OSError, match='connection reset'):
        await subscriber.run()


@pytest.mark.asyncio
async def test_the_prefetch_can_be_changed(fake_aio_pika):
    subscriber = RabbitMqSignalSubscriber(connection_for(fake_aio_pika), prefetch=1)
    subscriber.subscribe(TOPIC, 'sub', AsyncMock())

    await subscriber.run()

    fake_aio_pika.channel.set_qos.assert_awaited_once_with(prefetch_count=1)
