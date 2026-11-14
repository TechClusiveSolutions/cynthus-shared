"""Event Message Publisher class for the Cynthus project"""

from __future__ import annotations

from ...core.event import Event
from ..common.signal.message_base import SignalMessageBase
from ..registry import SignalGeneratorRegistry
from ..topic.signal_topic import SignalTopic
from .signal_publisher import SignalPublisher


class EventMessagePublisher:
    """
        Publishes the signal message of an event through any ``SignalPublisher``

        The registry finds the generator, the generator composes the message and the transport sends it. A lookup or
        generation error propagates and nothing is sent. Anyone holding a ready message calls the transport directly.
    """

    def __init__(self, transport: SignalPublisher, registry: SignalGeneratorRegistry | None = None) -> None:
        self._transport = transport
        self._registry = SignalGeneratorRegistry.default() if registry is None else registry

    async def publish(
        self, event: Event, access_token: str | None = None, *, topic: SignalTopic | None = None
    ) -> SignalMessageBase:
        """Generate the message for ``event``, publish it and return it (``message.event_type`` is the signal name)"""

        message = self._registry.generator_for(event).generate(event)

        await self._transport.publish(message, access_token, topic=topic)

        return message
