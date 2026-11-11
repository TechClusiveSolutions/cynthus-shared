"""RabbitMQ topology for the Cynthus project"""

from ..topic.signal_topic import SignalTopic

# What the Service Bus emulator configuration sets on every subscription: MaxDeliveryCount 10 and a one-hour TTL
DELIVERY_LIMIT = 10
MESSAGE_TTL_MILLISECONDS = 3_600_000

# A subscription with no filter receives every event type published to the topic
ALL_EVENTS = '#'


class RabbitMqTopology:
    """
        The names and queue settings that map a topic and its subscriptions onto RabbitMQ (ADR-007)

        A topic is a durable topic exchange of the same name; the routing key of a message is its event type. A
        subscription is a durable quorum queue of the same name. A signal that its handler rejects, or that is delivered
        more often than the delivery limit, is dead-lettered to ``<topic>.dlx`` (a direct exchange) with the subscription
        name as the routing key, and so reaches that subscription's own ``<subscription>.dlq`` queue and no other.
    """

    def __init__(self, delivery_limit: int = DELIVERY_LIMIT, message_ttl: int = MESSAGE_TTL_MILLISECONDS) -> None:
        self.delivery_limit = delivery_limit
        self.message_ttl = message_ttl

    @staticmethod
    def exchange(topic: SignalTopic) -> str:
        return topic.name

    @staticmethod
    def dead_letter_exchange(topic: SignalTopic) -> str:
        return f'{topic.name}.dlx'

    @staticmethod
    def dead_letter_queue(subscription: str) -> str:
        return f'{subscription}.dlq'

    def queue_arguments(self, topic: SignalTopic, subscription: str) -> dict:
        """The arguments a subscription's queue is declared with; RabbitMQ refuses a redeclaration that differs."""

        return {
            'x-queue-type': 'quorum',
            'x-delivery-limit': self.delivery_limit,
            'x-message-ttl': self.message_ttl,
            'x-dead-letter-exchange': self.dead_letter_exchange(topic),
            'x-dead-letter-routing-key': subscription,
        }

    @staticmethod
    def dead_letter_queue_arguments() -> dict:
        """Dead letters wait for a person to look at them, so they carry no TTL and no delivery limit."""

        return {'x-queue-type': 'quorum'}
