"""Tests for cynthus.messaging.rabbitmq.rabbitmq_connection (RabbitMqConnection)."""

import sys

import pytest

from cynthus.messaging.rabbitmq import RabbitMqConnection


def test_the_url_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv('RABBITMQ_URL', 'amqp://u:p@host:5672/vh')

    assert RabbitMqConnection.from_environment()._url == 'amqp://u:p@host:5672/vh'


def test_a_missing_url_is_a_clear_error_that_does_not_echo_anything_secret(monkeypatch):
    monkeypatch.delenv('RABBITMQ_URL', raising=False)

    with pytest.raises(ValueError, match='RABBITMQ_URL is not set'):
        RabbitMqConnection.from_environment()


@pytest.mark.asyncio
async def test_the_connection_opens_once_and_every_channel_shares_it(fake_aio_pika):
    connection = RabbitMqConnection('amqp://x')

    first = await connection.channel()
    second = await connection.channel()

    fake_aio_pika.module.connect_robust.assert_awaited_once_with('amqp://x')
    assert first is second is fake_aio_pika.channel
    assert fake_aio_pika.connection.channel.await_count == 2


@pytest.mark.asyncio
async def test_a_closed_connection_is_opened_again(fake_aio_pika):
    connection = RabbitMqConnection('amqp://x')

    await connection.channel()
    fake_aio_pika.connection.is_closed = True
    await connection.channel()

    assert fake_aio_pika.module.connect_robust.await_count == 2


@pytest.mark.asyncio
async def test_a_connection_that_is_reconnecting_reports_itself_as_a_connection_error(fake_aio_pika):
    fake_aio_pika.connection.channel.side_effect = RuntimeError('Connection was not opened')

    with pytest.raises(ConnectionError, match='reconnecting'):
        await RabbitMqConnection('amqp://x').channel()

    # The publisher treats OSError as "the broker cannot be reached", which gives SignalBusUnavailable
    assert OSError in RabbitMqConnection.errors() and issubclass(ConnectionError, OSError)


@pytest.mark.asyncio
async def test_closing_closes_the_connection_and_a_second_close_does_nothing(fake_aio_pika):
    connection = RabbitMqConnection('amqp://x')

    await connection.channel()
    await connection.close()
    await connection.close()

    fake_aio_pika.connection.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_closing_a_connection_that_never_opened_is_fine(fake_aio_pika):
    await RabbitMqConnection('amqp://x').close()

    fake_aio_pika.connection.close.assert_not_awaited()


def test_the_errors_include_the_networks_when_aio_pika_is_not_installed(fake_aio_pika):
    assert RabbitMqConnection.errors() == (OSError, TimeoutError)


def test_the_errors_include_the_brokers_when_aio_pika_is_installed(monkeypatch):
    class AMQPError(Exception):
        pass

    exceptions = type(sys)('aio_pika.exceptions')
    exceptions.AMQPError = AMQPError
    monkeypatch.setitem(sys.modules, 'aio_pika.exceptions', exceptions)

    assert RabbitMqConnection.errors() == (AMQPError, OSError, TimeoutError)
