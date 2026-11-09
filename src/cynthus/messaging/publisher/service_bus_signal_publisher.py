"""Service Bus signal publisher for the Cynthus project"""

import asyncio
import time
from os import environ

from azure.core.exceptions import ServiceRequestError
from azure.identity.aio import DefaultAzureCredential
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.exceptions import ServiceBusError

from cynthus.core import logging
from cynthus.messaging.topic import CoreSignalTopic, SignalTopic

from .signal_bus_unavailable import SignalBusUnavailable
from .signal_publisher import SignalPublisher

LOGGER = logging.getLogger(__name__)

AUTHORIZATION = 'authorization'

# What it looks like when the bus cannot be reached or refuses the connection (including its connection quota)
BUS_ERRORS = (ServiceBusError, ServiceRequestError, OSError, TimeoutError)

# The Azure SDK waits through long connect-and-retry delays before it gives up, which would leave a request (a sign-in,
# for one) hanging for minutes while the bus is down. Each attempt gets this long, and after a failure the publisher
# refuses at once for the cool-down, so the next callers learn of the outage immediately.
SEND_TIMEOUT_SECONDS = 5
COOLDOWN_SECONDS = 15
CLIENT_ATTRIBUTE = '_cynthus_signal_publisher'


class ServiceBusSignalPublisher(SignalPublisher):
    """Publishes `SignalMessage`s to the events topic, the way every service does it.

    One sender is kept open for the publisher's lifetime. Opening and closing a sender costs about a second on every
    message, which would make every acknowledgement slow; sending on an open sender takes tens of milliseconds.
    """

    def __init__(self, client: ServiceBusClient, credential=None) -> None:
        self._client = client
        self._credential = credential
        self._topic = CoreSignalTopic()
        self._sender = None
        self._opening = None
        self._sending = None
        # Told, with no arguments, when the bus turns out to be unreachable: a service uses it to report the outage
        self.on_unavailable = None
        self._down_until = 0.0

    @classmethod
    def for_client(cls, client: ServiceBusClient) -> 'ServiceBusSignalPublisher':
        """The publisher that belongs to `client`, created the first time it is asked for."""

        # Kept on the client itself: the publisher and the client refer to each other, and both go when the client does
        publisher = vars(client).get(CLIENT_ATTRIBUTE)

        if publisher is None:
            publisher = cls(client)
            setattr(client, CLIENT_ATTRIBUTE, publisher)

        return publisher

    @classmethod
    def from_environment(cls) -> 'ServiceBusSignalPublisher':
        """Uses SERVICE_BUS_CONNECTION_STRING (the emulator) or else SERVICE_BUS_NAMESPACE with Azure credentials."""

        connection_string = environ.get('SERVICE_BUS_CONNECTION_STRING')

        if connection_string:
            return cls(ServiceBusClient.from_connection_string(connection_string))

        credential = DefaultAzureCredential()

        return cls(
            ServiceBusClient(fully_qualified_namespace=environ.get('SERVICE_BUS_NAMESPACE'), credential=credential),
            credential,
        )

    async def publish(
        self, signal_message, access_token: str | None = None, *, topic: SignalTopic | None = None
    ) -> None:
        """`access_token` travels as the `authorization` message property, never in the body (which is logged)."""

        if topic is not None and topic.name != self._topic.name:
            raise ValueError(f'This publisher sends to {self._topic.name}, not {topic.name}')

        properties = {AUTHORIZATION: f'Bearer {access_token}'} if access_token else None

        def build() -> ServiceBusMessage:
            return ServiceBusMessage(
                body=signal_message.model_dump_json(),
                content_type='application/json',
                subject=signal_message.event_type,
                correlation_id=str(signal_message.correlation_id),
                application_properties=properties,
            )

        # A sender is not safe for concurrent sends: overlapping sends make one fail and shut the sender down for the
        # others, and each failure would then open (and orphan) another connection. One message at a time.
        try:
            async with self._send_lock():
                # Callers that queued behind a failing send must not each wait out their own attempts
                if time.monotonic() < self._down_until:
                    raise SignalBusUnavailable(f'The signal bus did not accept {signal_message.event_type} a moment ago')

                for attempt in (1, 2):
                    try:
                        await asyncio.wait_for(self._send(build), SEND_TIMEOUT_SECONDS)

                        return
                    except Exception:
                        if attempt == 2:
                            raise

                        # The link may have been dropped since the last message: start again on a fresh sender, once
                        LOGGER.getChild('publish').warning(
                            'Sending %s failed; retrying on a new sender', signal_message.event_type
                        )

                        await self._discard(self._sender)
        except BUS_ERRORS as error:
            # Only the type and the correlation id are logged: the body is never logged, and the error can name the namespace
            LOGGER.getChild('publish').warning(
                'The signal bus did not accept %s (correlation id %s)', signal_message.event_type,
                signal_message.correlation_id,
            )

            self._down_until = time.monotonic() + COOLDOWN_SECONDS

            await self._report_unavailable()

            raise SignalBusUnavailable(f'The signal bus did not accept {signal_message.event_type}') from error

    async def _send(self, build) -> None:
        sender = await self._open()
        await sender.send_messages(build())

    async def _report_unavailable(self) -> None:
        if self.on_unavailable is None:
            return

        try:
            await self.on_unavailable()
        except Exception:
            LOGGER.getChild('_report_unavailable').exception('Could not report that the signal bus is unavailable')

    async def close(self) -> None:
        await self._discard(self._sender)
        await self._client.close()

        if self._credential is not None:
            await self._credential.close()

    def _send_lock(self) -> asyncio.Lock:
        if self._sending is None:
            self._sending = asyncio.Lock()

        return self._sending

    def _lock(self) -> asyncio.Lock:
        # Created on first use so the publisher can be built before an event loop is running
        if self._opening is None:
            self._opening = asyncio.Lock()

        return self._opening

    async def _open(self):
        async with self._lock():
            if self._sender is None:
                sender = self._client.get_topic_sender(topic_name=self._topic.name)

                try:
                    await sender.__aenter__()
                except BaseException:
                    # A sender that failed to open still holds what it started; close it rather than orphan it
                    await self._close_quietly(sender)

                    raise

                self._sender = sender

            return self._sender

    async def _discard(self, sender) -> None:
        """Closes `sender`, which failed or is being retired, and forgets it only if it is still the current one."""

        async with self._lock():
            if self._sender is sender:
                self._sender = None

        if sender is not None:
            await self._close_quietly(sender)

    async def _close_quietly(self, sender) -> None:
        try:
            await sender.__aexit__(None, None, None)
        except Exception:
            LOGGER.getChild('_close_quietly').debug('The sender was already closed', exc_info=True)
