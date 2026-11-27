"""Event Request Approved Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .event_request_decision_answer import EventRequestDecisionAnswer
from .event_request_decision_event import EventRequestDecisionEvent


class DecisionEventRequestApprovedEvent(EventRequestDecisionEvent):
    """Represents the decision that an event request is approved"""

    answer: ClassVar[EventRequestDecisionAnswer | None] = EventRequestDecisionAnswer.APPROVED
