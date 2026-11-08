"""Signal Subscriber interface for the Cynthus project"""

from abc import ABC, abstractmethod

from ..topic.signal_topic import SignalTopic
from .signal_handler import SignalHandler


class SignalSubscriber(ABC):
    """
        Delivers the signals of subscriptions to handlers

        Register handlers with ``subscribe`` and then ``run`` until the task is cancelled. A handler that returns
        settles its signal; a handler that raises sends the signal to the dead-letter queue, so one bad signal does not
        block the ones behind it.
    """

    @abstractmethod
    def subscribe(self, topic: SignalTopic, subscription: str, handler: SignalHandler) -> None:
        """Call ``handler`` with every signal delivered to ``subscription`` on ``topic``."""

    @abstractmethod
    async def run(self) -> None:
        """Deliver signals to the registered handlers until cancelled."""
