"""Event Request Denied Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .event_request_decision_answer import EventRequestDecisionAnswer
from .event_request_decision_event import EventRequestDecisionEvent


class DecisionEventRequestDeniedEvent(EventRequestDecisionEvent):
    """Represents the decision that an event request is denied"""

    answer: ClassVar[EventRequestDecisionAnswer | None] = EventRequestDecisionAnswer.DENIED
