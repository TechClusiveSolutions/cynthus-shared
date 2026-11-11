"""RabbitMQ signal subscriber for the Cynthus project"""

import asyncio

from cynthus.core import logging
from cynthus.messaging.rabbitmq import RabbitMqConnection, RabbitMqTopology
from cynthus.messaging.rabbitmq.rabbitmq_topology import ALL_EVENTS

from ..topic.signal_topic import SignalTopic
from .received_signal import ReceivedSignal
from .signal_handler import SignalHandler
from .signal_subscriber import SignalSubscriber

LOGGER = logging.getLogger(__name__)

# How many unacknowledged signals the broker sends a subscription at once
PREFETCH = 10


class RabbitMqSignalSubscriber(SignalSubscriber):
    """
        Reads RabbitMQ queues, one per subscription, on channels of the connection the service already has

        A signal its handler accepts is acknowledged. A signal its handler raises on is rejected without requeueing, so
        the broker dead-letters it to ``<subscription>.dlq`` and the signals behind it are not blocked. Cancelling
        `run()` stops every loop without settling the signals in hand; the broker redelivers them.
    """

    def __init__(
        self, connection: RabbitMqConnection, topology: RabbitMqTopology | None = None, prefetch: int = PREFETCH
    ) -> None:
        self._connection = connection
        self._topology = topology or RabbitMqTopology()
        self._prefetch = prefetch
        self._registrations: list[tuple[SignalTopic, str, SignalHandler]] = []

    def subscribe(self, topic: SignalTopic, subscription: str, handler: SignalHandler) -> None:
        self._registrations.append((topic, subscription, handler))

    async def run(self) -> None:
        await asyncio.gather(*(self._read(*registration) for registration in self._registrations))

    async def _read(self, topic: SignalTopic, subscription: str, handler: SignalHandler) -> None:
        logger = LOGGER.getChild('_read')

        channel = await self._connection.channel()

        try:
            await channel.set_qos(prefetch_count=self._prefetch)

            queue = await self._declare(channel, topic, subscription)

            async with queue.iterator() as messages:
                async for message in messages:
                    try:
                        await handler(ReceivedSignal.from_rabbitmq(message))
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        logger.exception(
                            'Failed to process a signal; dead-lettering message %s', message.message_id
                        )

                        await message.reject(requeue=False)
                    else:
                        await message.ack()
        finally:
            await channel.close()

    async def _declare(self, channel, topic: SignalTopic, subscription: str):
        """Declares the exchange, the queue and its dead-letter queue, and binds them; every step is idempotent."""

        import aio_pika

        topology = self._topology

        try:
            dead_letters = await channel.declare_exchange(
                topology.dead_letter_exchange(topic), aio_pika.ExchangeType.DIRECT, durable=True
            )
            dead_letter_queue = await channel.declare_queue(
                topology.dead_letter_queue(subscription), durable=True,
                arguments=topology.dead_letter_queue_arguments(),
            )
            await dead_letter_queue.bind(dead_letters, routing_key=subscription)

            exchange = await channel.declare_exchange(
                topology.exchange(topic), aio_pika.ExchangeType.TOPIC, durable=True
            )
            queue = await channel.declare_queue(
                subscription, durable=True, arguments=topology.queue_arguments(topic, subscription)
            )
            await queue.bind(exchange, routing_key=ALL_EVENTS)
        except Exception as error:
            if 'PRECONDITION_FAILED' in str(error):
                # RabbitMQ refuses to redeclare a queue with other arguments (a changed delivery limit or TTL)
                raise RuntimeError(
                    f'The queue {subscription} already exists with different arguments; delete it or rename the '
                    f'subscription before changing its delivery limit or TTL'
                ) from error

            raise

        return queue
