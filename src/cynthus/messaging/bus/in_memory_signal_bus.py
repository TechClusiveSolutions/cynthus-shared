"""In-memory Signal Bus class for the Cynthus project"""

import logging

from ..common.signal.message_base import SignalMessageBase
from ..publisher.signal_publisher import SignalPublisher
from ..subscriber.signal_handler import SignalHandler
from ..subscriber.signal_subscriber import SignalSubscriber
from ..topic.core_signal_topic import CoreSignalTopic
from ..topic.signal_topic import SignalTopic
from .published_signal import PublishedSignal

LOGGER = logging.getLogger(__name__)


class InMemorySignalBus(SignalPublisher, SignalSubscriber):
    """
        A broker-free publisher and subscriber for unit tests and local runs

        Publishing records the signal and delivers its JSON body to every handler subscribed to the topic. A handler that
        raises does not stop the others and does not fail the publisher, mirroring a real bus where consumers fail
        independently; the error is kept in ``failures``.
    """

    def __init__(self) -> None:
        self.published: list[PublishedSignal] = []
        self.failures: list[tuple[str, Exception]] = []
        self._handlers: dict[str, list[tuple[str, SignalHandler]]] = {}

    def subscribe(self, topic: SignalTopic, subscription: str, handler: SignalHandler) -> None:
        self._handlers.setdefault(topic.name, []).append((subscription, handler))

    async def publish(
        self, message: SignalMessageBase, access_token: str | None = None, *, topic: SignalTopic | None = None
    ) -> None:
        topic = topic or CoreSignalTopic()
        self.published.append(PublishedSignal(topic_name=topic.name, message=message, access_token=access_token))
        body = message.model_dump(mode='json')

        for subscription, handler in list(self._handlers.get(topic.name, [])):
            try:
                await handler(body)
            except Exception as error:
                LOGGER.exception('Handler for subscription %s failed (correlation_id=%s)', subscription, message.correlation_id)
                self.failures.append((subscription, error))

    def published_to(self, topic: SignalTopic) -> list[SignalMessageBase]:
        """The messages published to ``topic``, oldest first."""

        return [signal.message for signal in self.published if signal.topic_name == topic.name]
