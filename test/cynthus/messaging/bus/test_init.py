"""Tests for cynthus.messaging.bus (the package initializer)."""


def test_exports_the_bus_and_the_recorded_signal():
    from cynthus.messaging import bus
    from cynthus.messaging.bus.in_memory_signal_bus import InMemorySignalBus
    from cynthus.messaging.bus.published_signal import PublishedSignal

    assert bus.InMemorySignalBus is InMemorySignalBus
    assert bus.PublishedSignal is PublishedSignal
