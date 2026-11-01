"""Tests for cynthus.messaging.subscriber.signal_subscriber (SignalSubscriber)."""

import pytest

from cynthus.messaging.subscriber.signal_subscriber import SignalSubscriber


def test_the_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        SignalSubscriber()


def test_subscribe_is_abstract():
    assert 'subscribe' in SignalSubscriber.__abstractmethods__


def test_a_subclass_implementing_subscribe_can_be_created():
    class Recording(SignalSubscriber):
        def subscribe(self, topic, subscription, handler):
            return None

    assert isinstance(Recording(), SignalSubscriber)
