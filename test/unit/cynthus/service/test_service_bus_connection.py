"""Tests for cynthus.service.service_bus_connection (ServiceBusConnection)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cynthus.service import service_bus_connection as module
from cynthus.service.service_bus_connection import ServiceBusConnection


def test_the_connection_string_is_used_when_present(monkeypatch):
    monkeypatch.setenv('SERVICE_BUS_CONNECTION_STRING', 'Endpoint=sb://x/;SharedAccessKey=k')

    with patch.object(module, 'ServiceBusClient') as client_class:
        connection = ServiceBusConnection.from_environment()

    client_class.from_connection_string.assert_called_once_with('Endpoint=sb://x/;SharedAccessKey=k')
    assert connection.client is client_class.from_connection_string.return_value


def test_azure_credentials_are_used_without_a_connection_string(monkeypatch):
    monkeypatch.delenv('SERVICE_BUS_CONNECTION_STRING', raising=False)
    monkeypatch.setenv('SERVICE_BUS_NAMESPACE', 'bus.test')

    with patch.object(module, 'ServiceBusClient') as client_class, \
            patch.object(module, 'DefaultAzureCredential') as credential_class:
        connection = ServiceBusConnection.from_environment()

    client_class.assert_called_once_with(
        fully_qualified_namespace='bus.test', credential=credential_class.return_value)
    assert connection.client is client_class.return_value


@pytest.mark.asyncio
async def test_closing_closes_the_client_and_the_credential():
    client, credential = MagicMock(), MagicMock()
    client.close, credential.close = AsyncMock(), AsyncMock()

    await ServiceBusConnection(client, credential).close()

    client.close.assert_awaited_once()
    credential.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_closing_without_a_credential_only_closes_the_client():
    client = MagicMock()
    client.close = AsyncMock()

    await ServiceBusConnection(client).close()

    client.close.assert_awaited_once()
