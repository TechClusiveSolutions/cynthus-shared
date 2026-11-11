"""Tests for cynthus.messaging.subscriber.signal_handler (SignalHandler)."""

import typing
from collections.abc import Awaitable, Callable

from cynthus.messaging.subscriber.received_signal import ReceivedSignal
from cynthus.messaging.subscriber.signal_handler import SignalHandler


def test_a_handler_is_an_async_callable_taking_a_received_signal():
    assert typing.get_origin(SignalHandler) is Callable
    arguments, result = typing.get_args(SignalHandler)

    assert arguments == [ReceivedSignal]
    assert typing.get_origin(result) is Awaitable
