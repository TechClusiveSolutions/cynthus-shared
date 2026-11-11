"""Integration tests against a real RabbitMQ. They run only when RABBITMQ_URL is set (ADR-007)."""

import asyncio
import os
import uuid
from types import SimpleNamespace

import pytest
import pytest_asyncio

from cynthus.messaging.publisher import RabbitMqSignalPublisher
from cynthus.messaging.rabbitmq import RabbitMqConnection
from cynthus.messaging.subscriber import RabbitMqSignalSubscriber
from cynthus.messaging.topic import CoreSignalTopic

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(not os.environ.get('RABBITMQ_URL'), reason='RABBITMQ_URL is not set'),
]

TIMEOUT = 15


def signal(event_type='public.integration.thing.created'):
    return SimpleNamespace(
        event_type=event_type, correlation_id=uuid.uuid4(), model_dump_json=lambda: '{"hello": "world"}'
    )


async def wait_for(condition):
    for _ in range(TIMEOUT * 10):
        value = await condition()

        if value:
            return value

        await asyncio.sleep(0.1)

    raise AssertionError('timed out waiting')


@pytest_asyncio.fixture
async def broker():
    name = f'it-{uuid.uuid4().hex[:12]}'
    connection = RabbitMqConnection.from_environment()
    publisher = RabbitMqSignalPublisher(connection)
    subscriber = RabbitMqSignalSubscriber(connection)
    admin = await connection.channel()

    yield SimpleNamespace(name=name, publisher=publisher, subscriber=subscriber, admin=admin)

    for queue in (name, f'{name}.dlq'):
        await admin.queue_delete(queue)

    await publisher.close()


async def queue_exists(broker):
    async def exists():
        try:
            channel = await broker.publisher._connection.channel()
            await channel.declare_queue(broker.name, passive=True)
        except Exception:
            return False

        return True

    return await wait_for(exists)


async def test_a_published_signal_reaches_the_subscription_with_its_token(broker):
    received = []

    async def handler(received_signal):
        received.append(received_signal)

    broker.subscriber.subscribe(CoreSignalTopic(), broker.name, handler)
    task = asyncio.create_task(broker.subscriber.run())

    try:
        await queue_exists(broker)
        await broker.publisher.publish(signal(), access_token='abc.def.ghi')
        await wait_for(lambda: asyncio.sleep(0, bool(received)))
    finally:
        task.cancel()

    assert received[0].event_type == 'public.integration.thing.created'
    assert received[0].payload == {'hello': 'world'}
    assert received[0].access_token == 'abc.def.ghi'
    assert received[0].correlation_id


async def test_a_signal_the_handler_raises_on_lands_in_the_subscriptions_dead_letter_queue(broker):
    async def handler(received_signal):
        raise RuntimeError('cannot handle')

    broker.subscriber.subscribe(CoreSignalTopic(), broker.name, handler)
    task = asyncio.create_task(broker.subscriber.run())

    try:
        await queue_exists(broker)
        await broker.publisher.publish(signal('public.integration.thing.bad'))

        async def dead_letter():
            queue = await broker.admin.declare_queue(f'{broker.name}.dlq', passive=True)

            return await queue.get(fail=False, no_ack=True)

        message = await wait_for(dead_letter)
    finally:
        task.cancel()

    assert message.type == 'public.integration.thing.bad'
    assert message.body == b'{"hello": "world"}'
