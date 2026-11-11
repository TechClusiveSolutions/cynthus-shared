"""Signal broker for the Cynthus project"""

from os import environ

from cynthus.core import logging
from cynthus.messaging.bus import InMemorySignalBus
from cynthus.messaging.publisher import RabbitMqSignalPublisher, ServiceBusSignalPublisher, SignalPublisher
from cynthus.messaging.rabbitmq import RabbitMqConnection
from cynthus.messaging.subscriber import RabbitMqSignalSubscriber, ServiceBusSignalSubscriber, SignalSubscriber

from .service_bus_connection import ServiceBusConnection

LOGGER = logging.getLogger(__name__)

SERVICE_BUS = 'servicebus'
RABBITMQ = 'rabbitmq'
MEMORY = 'memory'
BROKERS = (SERVICE_BUS, RABBITMQ, MEMORY)


class SignalBroker:
    """
        The broker a process uses, chosen by the ``SIGNAL_BROKER`` environment variable (ADR-007)

        ``servicebus`` (the default) uses Azure Service Bus with ``SERVICE_BUS_CONNECTION_STRING`` or
        ``SERVICE_BUS_NAMESPACE``; ``rabbitmq`` uses ``RABBITMQ_URL``; ``memory`` keeps signals inside the process, for
        tests and local runs. Whichever it is, the process gets one ``publisher``, one ``subscriber`` and the single
        connection they share (``client``), and service code never names a broker.
    """

    def __init__(self, name: str, publisher: SignalPublisher, subscriber: SignalSubscriber, client, connection=None):
        self.name = name
        self.publisher = publisher
        self.subscriber = subscriber
        self.client = client
        self._connection = connection

    @classmethod
    def from_environment(cls) -> 'SignalBroker':
        name = environ.get('SIGNAL_BROKER', SERVICE_BUS).strip().lower() or SERVICE_BUS

        LOGGER.getChild('from_environment').info('Using the %s signal broker', name)

        if name == SERVICE_BUS:
            connection = ServiceBusConnection.from_environment()

            return cls(
                name, ServiceBusSignalPublisher.for_client(connection.client),
                ServiceBusSignalSubscriber(connection.client), connection.client, connection,
            )

        if name == RABBITMQ:
            connection = RabbitMqConnection.from_environment()

            return cls(
                name, RabbitMqSignalPublisher(connection), RabbitMqSignalSubscriber(connection), connection, connection,
            )

        if name == MEMORY:
            bus = InMemorySignalBus()

            return cls(name, bus, bus, None)

        raise ValueError(f'SIGNAL_BROKER is {name!r}; it must be one of: {", ".join(BROKERS)}')

    async def close(self) -> None:
        """Closes the publisher and then the connection; the connection closes even if the publisher cannot."""

        try:
            close = getattr(self.publisher, 'close', None)

            if close is not None:
                await close()
        finally:
            if self._connection is not None:
                await self._connection.close()
