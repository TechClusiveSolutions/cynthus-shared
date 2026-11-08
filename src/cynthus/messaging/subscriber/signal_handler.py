"""Signal Handler type for the Cynthus project"""

from collections.abc import Awaitable, Callable

from .received_signal import ReceivedSignal

SignalHandler = Callable[[ReceivedSignal], Awaitable[None]]
"""An async callable that receives one signal. Returning settles it; raising dead-letters it."""
