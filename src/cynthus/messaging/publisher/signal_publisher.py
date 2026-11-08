"""Signal Publisher interface for the Cynthus project"""

from abc import ABC, abstractmethod

from ..common.signal.message_base import SignalMessageBase
from ..topic.signal_topic import SignalTopic


class SignalPublisher(ABC):
    """
        Publishes signal messages to a topic

        Application code depends on this interface, never on a broker class (ADR-006).
    """

    @abstractmethod
    async def publish(
        self, message: SignalMessageBase, access_token: str | None = None, *, topic: SignalTopic | None = None
    ) -> None:
        """
            Publish ``message`` to ``topic`` (the core signal topic when omitted)

            ``access_token`` travels with the message as the ``authorization`` property, never in its body. Must not
            return before the broker has accepted the message.
        """
