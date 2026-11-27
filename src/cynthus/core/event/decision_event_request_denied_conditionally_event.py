"""Event Request Denied Conditionally Event class for the Cynthus project"""

from __future__ import annotations

from .event_request_decision_event import EventRequestDecisionEvent


class DecisionEventRequestDeniedConditionallyEvent(EventRequestDecisionEvent):
    """Represents the decision that an event request is denied unless its conditions are met"""
