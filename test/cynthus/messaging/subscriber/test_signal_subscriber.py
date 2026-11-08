"""Tests for cynthus.messaging.subscriber.signal_subscriber (SignalSubscriber)."""

import pytest

from cynthus.messaging.subscriber.signal_subscriber import SignalSubscriber


def test_the_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        SignalSubscriber()


def test_subscribe_and_run_are_abstract():
    assert {'subscribe', 'run'} <= SignalSubscriber.__abstractmethods__


def test_a_subclass_implementing_both_can_be_created():
    class Recording(SignalSubscriber):
        def subscribe(self, topic, subscription, handler):
            return None

        async def run(self):
            return None

    assert isinstance(Recording(), SignalSubscriber)
