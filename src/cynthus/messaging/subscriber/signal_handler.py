"""Signal Handler type for the Cynthus project"""

from collections.abc import Awaitable, Callable
from typing import Any

SignalHandler = Callable[[dict[str, Any]], Awaitable[None]]
"""An async callable that receives the decoded JSON body of one signal."""
