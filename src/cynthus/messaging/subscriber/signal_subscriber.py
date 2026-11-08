"""Signal Subscriber interface for the Cynthus project"""

from abc import ABC, abstractmethod

from ..topic.signal_topic import SignalTopic
from .signal_handler import SignalHandler


class SignalSubscriber(ABC):
    """Registers handlers for the signals arriving on one subscription of a topic."""

    @abstractmethod
    def subscribe(self, topic: SignalTopic, subscription: str, handler: SignalHandler) -> None:
        """Call ``handler`` with the decoded body of every signal delivered to ``subscription`` on ``topic``."""
