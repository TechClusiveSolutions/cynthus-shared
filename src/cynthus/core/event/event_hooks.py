"""Event Hooks class for the Cynthus project"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from .. import logging

LOGGER = logging.getLogger(__name__)


class EventHooks:
    """Holds the hooks to run when an event happens, keyed by event class"""

    def __init__(self) -> None:
        self._hooks: list[tuple[type, Callable[[Any], Awaitable[None]]]] = []

    def register(self, event_class: type, hook: Callable[[Any], Awaitable[None]]) -> None:
        """Run ``hook`` for every event that is an instance of ``event_class`` (a subclass counts)"""

        self._hooks.append((event_class, hook))

    async def fire(self, event: Any) -> None:
        """
            Await, in registration order, every hook registered for the class of ``event`` or a base class of it

            A hook that raises is logged and the next one still runs; cancellation is never swallowed.
        """

        for event_class, hook in list(self._hooks):
            if not isinstance(event, event_class):
                continue

            try:
                await hook(event)
            except Exception:
                LOGGER.exception('Event hook %r failed for event type %s', hook, _event_type(event))


def _event_type(event: Any) -> str:
    return getattr(event, 'event_type', type(event).__name__)
