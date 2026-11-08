"""Tests for cynthus.messaging.publisher.signal_publisher (SignalPublisher)."""

import inspect

import pytest

from cynthus.messaging.publisher.signal_publisher import SignalPublisher


def test_the_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        SignalPublisher()


def test_publish_is_an_abstract_coroutine():
    assert 'publish' in SignalPublisher.__abstractmethods__
    assert inspect.iscoroutinefunction(SignalPublisher.publish)


def test_a_subclass_implementing_publish_can_be_created():
    class Recording(SignalPublisher):
        async def publish(self, message, access_token=None, *, topic=None):
            return None

    assert isinstance(Recording(), SignalPublisher)
