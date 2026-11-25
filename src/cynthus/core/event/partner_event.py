"""Partner Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .event_action import EventAction
from .signal_event import SignalEvent


class PartnerEvent(SignalEvent):
    """Represents an action asked of the Partner service; both of its events are reads"""

    actions: ClassVar[frozenset[EventAction] | None] = frozenset({EventAction.RETRIEVED})
