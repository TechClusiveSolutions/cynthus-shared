"""RabbitMQ signal publisher for the Cynthus project"""

import asyncio
import time
from uuid import uuid4

from cynthus.core import logging
from cynthus.messaging.rabbitmq import RabbitMqConnection, RabbitMqTopology
from cynthus.messaging.topic import CoreSignalTopic, SignalTopic

from .signal_bus_unavailable import SignalBusUnavailable
from .signal_publisher import SignalPublisher

LOGGER = logging.getLogger(__name__)

AUTHORIZATION = 'authorization'

# The same limits as the Service Bus publisher: each attempt gets this long, and after a failure the publisher refuses at
# once for the cool-down, so a request does not hang while the broker is down and the next callers learn of it at once.
SEND_TIMEOUT_SECONDS = 5
COOLDOWN_SECONDS = 15


class RabbitMqSignalPublisher(SignalPublisher):
    """
        Publishes `SignalMessage`s to the events exchange, the way `ServiceBusSignalPublisher` does

        The routing key is the event type. The channel confirms each message, so ``publish`` does not return before the
        broker has accepted it. One channel is kept open for the publisher's lifetime and one message is sent at a time.
    """

    def __init__(self, connection: RabbitMqConnection, topology: RabbitMqTopology | None = None) -> None:
        self._connection = connection
        self._topology = topology or RabbitMqTopology()
        self._topic = CoreSignalTopic()
        self._channel = None
        self._exchange = None
        self._opening = None
        self._sending = None
        # Told, with no arguments, when the broker turns out to be unreachable: a service uses it to report the outage
        self.on_unavailable = None
        self._down_until = 0.0

    async def publish(
        self, signal_message, access_token: str | None = None, *, topic: SignalTopic | None = None
    ) -> None:
        """`access_token` travels as the `authorization` header, never in the body (which is logged)."""

        if topic is not None and topic.name != self._topic.name:
            raise ValueError(f'This publisher sends to {self._topic.name}, not {topic.name}')

        headers = {AUTHORIZATION: f'Bearer {access_token}'} if access_token else None

        try:
            async with self._send_lock():
                # Callers that queued behind a failing send must not each wait out their own attempts
                if time.monotonic() < self._down_until:
                    raise SignalBusUnavailable(f'The signal bus did not accept {signal_message.event_type} a moment ago')

                for attempt in (1, 2):
                    try:
                        await asyncio.wait_for(self._send(signal_message, headers), SEND_TIMEOUT_SECONDS)

                        return
                    except Exception:
                        if attempt == 2:
                            raise

                        # The channel may have been dropped since the last message: start again on a fresh one, once
                        LOGGER.getChild('publish').warning(
                            'Sending %s failed; retrying on a new channel', signal_message.event_type
                        )

                        await self._discard()
        except (*RabbitMqConnection.errors(), asyncio.TimeoutError) as error:
            # Only the type and the correlation id are logged: the body is never logged, and the error can name the host
            LOGGER.getChild('publish').warning(
                'The signal bus did not accept %s (correlation id %s)', signal_message.event_type,
                signal_message.correlation_id,
            )

            self._down_until = time.monotonic() + COOLDOWN_SECONDS

            await self._report_unavailable()

            raise SignalBusUnavailable(f'The signal bus did not accept {signal_message.event_type}') from error

    async def close(self) -> None:
        await self._discard()
        await self._connection.close()

    async def _send(self, signal_message, headers) -> None:
        import aio_pika

        exchange = await self._open()

        message = aio_pika.Message(
            body=signal_message.model_dump_json().encode('utf-8'),
            content_type='application/json',
            type=signal_message.event_type,
            message_id=uuid4().hex,
            correlation_id=str(signal_message.correlation_id),
            headers=headers,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await exchange.publish(message, routing_key=signal_message.event_type)

    async def _report_unavailable(self) -> None:
        if self.on_unavailable is None:
            return

        try:
            await self.on_unavailable()
        except Exception:
            LOGGER.getChild('_report_unavailable').exception('Could not report that the signal bus is unavailable')

    def _send_lock(self) -> asyncio.Lock:
        # Created on first use so the publisher can be built before an event loop is running
        if self._sending is None:
            self._sending = asyncio.Lock()

        return self._sending

    def _lock(self) -> asyncio.Lock:
        if self._opening is None:
            self._opening = asyncio.Lock()

        return self._opening

    async def _open(self):
        import aio_pika

        async with self._lock():
            if self._exchange is None:
                channel = await self._connection.channel()

                try:
                    self._exchange = await channel.declare_exchange(
                        self._topology.exchange(self._topic), aio_pika.ExchangeType.TOPIC, durable=True
                    )
                except BaseException:
                    # A channel that failed to set up holds what it started; close it rather than orphan it
                    await self._close_quietly(channel)

                    raise

                self._channel = channel

            return self._exchange

    async def _discard(self) -> None:
        """Closes the channel, which failed or is being retired, so the next message opens a fresh one."""

        async with self._lock():
            channel, self._channel, self._exchange = self._channel, None, None

        if channel is not None:
            await self._close_quietly(channel)

    async def _close_quietly(self, channel) -> None:
        try:
            await channel.close()
        except Exception:
            LOGGER.getChild('_close_quietly').debug('The channel was already closed', exc_info=True)
