"""Tests for cynthus.messaging.publisher.signal_bus_unavailable (SignalBusUnavailable)."""

from cynthus.messaging.publisher import SignalBusUnavailable
from cynthus.messaging.publisher.signal_bus_unavailable import SignalBusUnavailable as FromModule


def test_it_is_an_exception_exported_by_the_package():
    assert SignalBusUnavailable is FromModule
    assert issubclass(SignalBusUnavailable, Exception)


def test_it_keeps_the_message_it_is_given():
    assert str(SignalBusUnavailable('the bus is down')) == 'the bus is down'
