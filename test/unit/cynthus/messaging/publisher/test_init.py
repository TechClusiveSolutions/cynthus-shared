"""Tests for cynthus.messaging.publisher (the package initializer)."""


def test_exports_the_signal_publisher():
    from cynthus.messaging import publisher
    from cynthus.messaging.publisher.signal_publisher import SignalPublisher

    assert publisher.SignalPublisher is SignalPublisher
