"""Service Bus connection for the Cynthus project"""

from os import environ

from azure.identity.aio import DefaultAzureCredential
from azure.servicebus.aio import ServiceBusClient


class ServiceBusConnection:
    """
        The one Service Bus client of a process, with the credential that opened it (if any)

        The publisher and the subscriber share this client, so a service holds as few broker connections as it can.
    """

    def __init__(self, client: ServiceBusClient, credential=None) -> None:
        self.client = client
        self._credential = credential

    @classmethod
    def from_environment(cls) -> 'ServiceBusConnection':
        """Uses SERVICE_BUS_CONNECTION_STRING (the emulator) or else SERVICE_BUS_NAMESPACE with Azure credentials."""

        connection_string = environ.get('SERVICE_BUS_CONNECTION_STRING')

        if connection_string:
            return cls(ServiceBusClient.from_connection_string(connection_string))

        credential = DefaultAzureCredential()

        return cls(
            ServiceBusClient(fully_qualified_namespace=environ.get('SERVICE_BUS_NAMESPACE'), credential=credential),
            credential,
        )

    async def close(self) -> None:
        await self.client.close()

        if self._credential is not None:
            await self._credential.close()
