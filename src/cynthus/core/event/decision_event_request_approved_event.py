"""Event Request Approved Event class for the Cynthus project"""

from __future__ import annotations

from .event_request_decision_event import EventRequestDecisionEvent


class DecisionEventRequestApprovedEvent(EventRequestDecisionEvent):
    """Represents the decision that an event request is approved"""
