"""Tests for cynthus.messaging.subscriber (the package initializer)."""


def test_exports_the_interface_and_the_handler_type():
    from cynthus.messaging import subscriber
    from cynthus.messaging.subscriber.signal_handler import SignalHandler
    from cynthus.messaging.subscriber.signal_subscriber import SignalSubscriber

    assert subscriber.SignalSubscriber is SignalSubscriber
    assert subscriber.SignalHandler is SignalHandler
