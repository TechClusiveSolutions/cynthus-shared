"""Tests for cynthus.service.signal_broker (SignalBroker)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cynthus.messaging.bus import InMemorySignalBus
from cynthus.messaging.publisher import RabbitMqSignalPublisher
from cynthus.messaging.subscriber import RabbitMqSignalSubscriber
from cynthus.service import SignalBroker
from cynthus.service import signal_broker as module


def test_service_bus_is_the_default(monkeypatch):
    monkeypatch.delenv('SIGNAL_BROKER', raising=False)
    connection = MagicMock()

    with patch.object(module.ServiceBusConnection, 'from_environment', return_value=connection), \
            patch.object(module.ServiceBusSignalPublisher, 'for_client') as for_client, \
            patch.object(module, 'ServiceBusSignalSubscriber') as subscriber_class:
        broker = SignalBroker.from_environment()

    assert broker.name == 'servicebus'
    for_client.assert_called_once_with(connection.client)
    subscriber_class.assert_called_once_with(connection.client)
    assert broker.publisher is for_client.return_value
    assert broker.subscriber is subscriber_class.return_value
    assert broker.client is connection.client


@pytest.mark.parametrize('value', ['servicebus', ' ServiceBus ', ''])
def test_service_bus_is_chosen_whatever_the_case_and_when_the_setting_is_blank(monkeypatch, value):
    monkeypatch.setenv('SIGNAL_BROKER', value)

    with patch.object(module.ServiceBusConnection, 'from_environment'), \
            patch.object(module.ServiceBusSignalPublisher, 'for_client'), \
            patch.object(module, 'ServiceBusSignalSubscriber'):
        assert SignalBroker.from_environment().name == 'servicebus'


def test_rabbitmq_builds_the_connection_the_publisher_and_the_subscriber(monkeypatch):
    monkeypatch.setenv('SIGNAL_BROKER', 'rabbitmq')
    monkeypatch.setenv('RABBITMQ_URL', 'amqp://u:p@host:5672/vh')

    broker = SignalBroker.from_environment()

    assert broker.name == 'rabbitmq'
    assert isinstance(broker.publisher, RabbitMqSignalPublisher)
    assert isinstance(broker.subscriber, RabbitMqSignalSubscriber)
    assert broker.publisher._connection is broker.subscriber._connection is broker.client


def test_rabbitmq_without_a_url_fails_at_start_up(monkeypatch):
    monkeypatch.setenv('SIGNAL_BROKER', 'rabbitmq')
    monkeypatch.delenv('RABBITMQ_URL', raising=False)

    with pytest.raises(ValueError, match='RABBITMQ_URL'):
        SignalBroker.from_environment()


def test_memory_is_one_bus_that_both_publishes_and_subscribes(monkeypatch):
    monkeypatch.setenv('SIGNAL_BROKER', 'memory')

    broker = SignalBroker.from_environment()

    assert isinstance(broker.publisher, InMemorySignalBus)
    assert broker.publisher is broker.subscriber
    assert broker.client is None


def test_an_unknown_broker_names_the_choices(monkeypatch):
    monkeypatch.setenv('SIGNAL_BROKER', 'kafka')

    with pytest.raises(ValueError, match="'kafka'.*servicebus, rabbitmq, memory"):
        SignalBroker.from_environment()


@pytest.mark.asyncio
async def test_closing_closes_the_publisher_and_then_the_connection():
    order = []
    publisher, connection = MagicMock(), MagicMock()
    publisher.close = AsyncMock(side_effect=lambda: order.append('publisher'))
    connection.close = AsyncMock(side_effect=lambda: order.append('connection'))

    await SignalBroker('x', publisher, MagicMock(), None, connection).close()

    assert order == ['publisher', 'connection']


@pytest.mark.asyncio
async def test_the_connection_closes_even_when_the_publisher_cannot():
    publisher, connection = MagicMock(), MagicMock()
    publisher.close = AsyncMock(side_effect=RuntimeError('boom'))
    connection.close = AsyncMock()

    with pytest.raises(RuntimeError, match='boom'):
        await SignalBroker('x', publisher, MagicMock(), None, connection).close()

    connection.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_closing_a_broker_with_nothing_to_close_is_fine(monkeypatch):
    monkeypatch.setenv('SIGNAL_BROKER', 'memory')

    await SignalBroker.from_environment().close()
