"""Tests for cynthus.messaging.publisher.rabbitmq_signal_publisher (RabbitMqSignalPublisher)."""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from cynthus.messaging.publisher import RabbitMqSignalPublisher, SignalBusUnavailable, SignalPublisher
from cynthus.messaging.publisher import rabbitmq_signal_publisher as publisher_module
from cynthus.messaging.rabbitmq import RabbitMqConnection
from cynthus.messaging.topic import CoreSignalTopic, SignalTopic


def _connection(fake):
    connection = MagicMock(spec=RabbitMqConnection)
    connection.channel = AsyncMock(return_value=fake.channel)
    connection.close = AsyncMock()

    return connection


def _message():
    message = MagicMock()
    message.model_dump_json.return_value = '{"event_type": "audit.identity.token.issued"}'
    message.event_type = 'audit.identity.token.issued'
    message.correlation_id = 'corr-1'

    return message


def test_it_is_a_signal_publisher(fake_aio_pika):
    assert isinstance(RabbitMqSignalPublisher(_connection(fake_aio_pika)), SignalPublisher)


@pytest.mark.asyncio
async def test_a_signal_goes_to_the_events_exchange_routed_by_its_event_type(fake_aio_pika):
    await RabbitMqSignalPublisher(_connection(fake_aio_pika)).publish(_message())

    fake_aio_pika.channel.declare_exchange.assert_awaited_once_with('cynthus-events-topic', 'topic', durable=True)

    sent, = fake_aio_pika.exchange.publish.await_args.args
    assert fake_aio_pika.exchange.publish.await_args.kwargs == {'routing_key': 'audit.identity.token.issued'}
    assert sent.body == b'{"event_type": "audit.identity.token.issued"}'
    assert sent.type == 'audit.identity.token.issued'
    assert sent.correlation_id == 'corr-1'
    assert sent.content_type == 'application/json'
    assert sent.delivery_mode == 2
    assert sent.headers is None
    assert len(sent.message_id) == 32


@pytest.mark.asyncio
async def test_the_callers_token_travels_as_a_header_never_in_the_body(fake_aio_pika):
    await RabbitMqSignalPublisher(_connection(fake_aio_pika)).publish(_message(), access_token='abc.def.ghi')

    sent, = fake_aio_pika.exchange.publish.await_args.args

    assert sent.headers == {'authorization': 'Bearer abc.def.ghi'}
    assert b'abc.def.ghi' not in sent.body


@pytest.mark.asyncio
async def test_the_channel_and_exchange_are_opened_once_for_many_signals(fake_aio_pika):
    publisher = RabbitMqSignalPublisher(_connection(fake_aio_pika))

    for _ in range(3):
        await publisher.publish(_message())

    assert fake_aio_pika.exchange.publish.await_count == 3
    fake_aio_pika.channel.declare_exchange.assert_awaited_once()


@pytest.mark.asyncio
async def test_another_topic_is_refused(fake_aio_pika):
    with pytest.raises(ValueError, match='cynthus-events-topic'):
        await RabbitMqSignalPublisher(_connection(fake_aio_pika)).publish(_message(), topic=SignalTopic(name='other'))


@pytest.mark.asyncio
async def test_the_core_topic_may_be_named_explicitly(fake_aio_pika):
    await RabbitMqSignalPublisher(_connection(fake_aio_pika)).publish(_message(), topic=CoreSignalTopic())

    fake_aio_pika.exchange.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_a_failed_send_is_retried_once_on_a_new_channel(fake_aio_pika):
    fake_aio_pika.exchange.publish.side_effect = [OSError('dropped'), None]
    publisher = RabbitMqSignalPublisher(_connection(fake_aio_pika))

    await publisher.publish(_message())

    assert fake_aio_pika.exchange.publish.await_count == 2
    fake_aio_pika.channel.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_two_failures_raise_signal_bus_unavailable_and_report_it_once(fake_aio_pika):
    fake_aio_pika.exchange.publish.side_effect = OSError('down')
    publisher = RabbitMqSignalPublisher(_connection(fake_aio_pika))
    publisher.on_unavailable = AsyncMock()

    with pytest.raises(SignalBusUnavailable) as error:
        await publisher.publish(_message())

    assert isinstance(error.value.__cause__, OSError)
    publisher.on_unavailable.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_after_a_failure_callers_are_refused_at_once_without_touching_the_broker(fake_aio_pika):
    fake_aio_pika.exchange.publish.side_effect = OSError('down')
    publisher = RabbitMqSignalPublisher(_connection(fake_aio_pika))

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())

    attempts = fake_aio_pika.exchange.publish.await_count

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())

    assert fake_aio_pika.exchange.publish.await_count == attempts


@pytest.mark.asyncio
async def test_the_cool_down_ends_and_sending_resumes(fake_aio_pika):
    fake_aio_pika.exchange.publish.side_effect = OSError('down')
    publisher = RabbitMqSignalPublisher(_connection(fake_aio_pika))

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())

    fake_aio_pika.exchange.publish.side_effect = None
    publisher._down_until = time.monotonic() - 1

    await publisher.publish(_message())


@pytest.mark.asyncio
async def test_a_send_that_takes_too_long_counts_as_a_failure(fake_aio_pika, monkeypatch):
    import asyncio

    async def never(*args, **kwargs):
        await asyncio.sleep(10)

    monkeypatch.setattr(publisher_module, 'SEND_TIMEOUT_SECONDS', 0.01)
    fake_aio_pika.exchange.publish.side_effect = never

    with pytest.raises(SignalBusUnavailable):
        await RabbitMqSignalPublisher(_connection(fake_aio_pika)).publish(_message())


@pytest.mark.asyncio
async def test_a_failing_unavailable_report_does_not_hide_the_outage(fake_aio_pika):
    fake_aio_pika.exchange.publish.side_effect = OSError('down')
    publisher = RabbitMqSignalPublisher(_connection(fake_aio_pika))
    publisher.on_unavailable = AsyncMock(side_effect=RuntimeError('redis is down too'))

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())


@pytest.mark.asyncio
async def test_an_error_that_is_not_a_broker_error_is_not_an_outage(fake_aio_pika):
    fake_aio_pika.exchange.publish.side_effect = RuntimeError('a bug')

    with pytest.raises(RuntimeError, match='a bug'):
        await RabbitMqSignalPublisher(_connection(fake_aio_pika)).publish(_message())


@pytest.mark.asyncio
async def test_a_channel_that_cannot_set_up_is_closed_not_orphaned(fake_aio_pika):
    fake_aio_pika.channel.declare_exchange.side_effect = OSError('no')

    with pytest.raises(SignalBusUnavailable):
        await RabbitMqSignalPublisher(_connection(fake_aio_pika)).publish(_message())

    assert fake_aio_pika.channel.close.await_count >= 1


@pytest.mark.asyncio
async def test_closing_closes_the_channel_and_the_connection(fake_aio_pika):
    connection = _connection(fake_aio_pika)
    publisher = RabbitMqSignalPublisher(connection)

    await publisher.publish(_message())
    await publisher.close()

    fake_aio_pika.channel.close.assert_awaited_once()
    connection.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_closing_survives_a_channel_that_is_already_closed(fake_aio_pika):
    fake_aio_pika.channel.close.side_effect = RuntimeError('already closed')
    connection = _connection(fake_aio_pika)
    publisher = RabbitMqSignalPublisher(connection)

    await publisher.publish(_message())
    await publisher.close()

    connection.close.assert_awaited_once()
