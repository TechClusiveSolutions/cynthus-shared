"""Tests for cynthus.messaging.subscriber (the package initializer)."""


def test_exports_the_interface_the_adapter_the_signal_and_the_handler_type():
    from cynthus.messaging import subscriber
    from cynthus.messaging.subscriber.received_signal import ReceivedSignal
    from cynthus.messaging.subscriber.service_bus_signal_subscriber import ServiceBusSignalSubscriber
    from cynthus.messaging.subscriber.signal_handler import SignalHandler
    from cynthus.messaging.subscriber.signal_subscriber import SignalSubscriber

    assert subscriber.SignalSubscriber is SignalSubscriber
    assert subscriber.SignalHandler is SignalHandler
    assert subscriber.ReceivedSignal is ReceivedSignal
    assert subscriber.ServiceBusSignalSubscriber is ServiceBusSignalSubscriber
