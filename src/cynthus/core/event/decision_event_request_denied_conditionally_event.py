"""Event Request Denied Conditionally Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .event_request_decision_answer import EventRequestDecisionAnswer
from .event_request_decision_event import EventRequestDecisionEvent


class DecisionEventRequestDeniedConditionallyEvent(EventRequestDecisionEvent):
    """Represents the decision that an event request is denied unless its conditions are met"""

    answer: ClassVar[EventRequestDecisionAnswer | None] = EventRequestDecisionAnswer.DENIED_CONDITIONALLY
