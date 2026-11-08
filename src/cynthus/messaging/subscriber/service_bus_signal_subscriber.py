"""Service Bus signal subscriber for the Cynthus project"""

import asyncio

from ..topic.signal_topic import SignalTopic
from .received_signal import ReceivedSignal
from .signal_handler import SignalHandler
from .signal_subscriber import SignalSubscriber


class ServiceBusSignalSubscriber(SignalSubscriber):
    """
        Receives from Azure Service Bus subscriptions with the client the service already has

        Each subscription is read by a `SignalConsumer`, which completes what the handler accepts and dead-letters what
        it raises on. Cancelling `run()` stops every loop without settling the signals in hand; the broker redelivers.
    """

    def __init__(self, client) -> None:
        self._client = client
        self._registrations: list[tuple[SignalTopic, str, SignalHandler]] = []

    def subscribe(self, topic: SignalTopic, subscription: str, handler: SignalHandler) -> None:
        self._registrations.append((topic, subscription, handler))

    async def run(self) -> None:
        # Imported here: cynthus.service imports the messaging package, which imports this module
        from cynthus.service.signal_consumer import SignalConsumer

        def adapt(handler: SignalHandler):
            async def handle(message) -> None:
                await handler(ReceivedSignal.from_service_bus(message))

            return handle

        consumers = [
            SignalConsumer(self._client, subscription, adapt(handler), topic_name=topic.name)
            for topic, subscription, handler in self._registrations
        ]

        await asyncio.gather(*(consumer.run() for consumer in consumers))
