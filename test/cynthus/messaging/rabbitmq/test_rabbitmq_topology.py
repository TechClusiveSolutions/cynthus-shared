"""Tests for cynthus.messaging.rabbitmq.rabbitmq_topology (RabbitMqTopology)."""

from cynthus.messaging.rabbitmq import RabbitMqTopology
from cynthus.messaging.topic import CoreSignalTopic


def test_the_topic_is_an_exchange_of_the_same_name_with_a_dead_letter_exchange_beside_it():
    topology = RabbitMqTopology()

    assert topology.exchange(CoreSignalTopic()) == 'cynthus-events-topic'
    assert topology.dead_letter_exchange(CoreSignalTopic()) == 'cynthus-events-topic.dlx'


def test_each_subscription_has_its_own_dead_letter_queue():
    assert RabbitMqTopology().dead_letter_queue('cynthus-profile-sub') == 'cynthus-profile-sub.dlq'


def test_a_subscription_queue_matches_the_service_bus_limits_and_dead_letters_to_its_own_queue():
    arguments = RabbitMqTopology().queue_arguments(CoreSignalTopic(), 'cynthus-profile-sub')

    assert arguments == {
        'x-queue-type': 'quorum',
        'x-delivery-limit': 10,
        'x-message-ttl': 3_600_000,
        'x-dead-letter-exchange': 'cynthus-events-topic.dlx',
        'x-dead-letter-routing-key': 'cynthus-profile-sub',
    }


def test_the_limits_can_be_changed():
    arguments = RabbitMqTopology(delivery_limit=3, message_ttl=1000).queue_arguments(CoreSignalTopic(), 's')

    assert arguments['x-delivery-limit'] == 3
    assert arguments['x-message-ttl'] == 1000


def test_dead_letters_never_expire_and_have_no_delivery_limit():
    assert RabbitMqTopology.dead_letter_queue_arguments() == {'x-queue-type': 'quorum'}
