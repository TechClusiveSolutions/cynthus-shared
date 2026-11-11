"""Event Request Response class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional

from .event_request import EventRequest
from .event_request_decision import EventRequestDecision


class EventRequestResponse(BaseModel):
    """Represents the response to an event request"""

    request: EventRequest
    decision: EventRequestDecision


    def approve(self, reason: EventRequestDecisionReason) -> EventRequestDecision:
        """Approve the requested event request"""

        self.decision = EventRequestDecision(answer='approved', reason=reason)

        return self.decision


    def conditionally_approve(self, reason: EventRequestDecisionReason, condition: EventRequestDecisionCondition) -> EventRequestDecision:
        """Conditionally approve the requested event request"""

        self.decision = EventRequestDecision(answer='approved_conditionally', reason=reason, condition=condition)

        return self.decision


    def deny(self, reason: EventRequestDecisionReason) -> EventRequestDecision:
        """Deny the requested event request"""

        self.decision = EventRequestDecision(answer='denied', reason=reason)

        return self.decision


    def conditionally_deny(self, reason: EventRequestDecisionReason, condition: EventRequestDecisionCondition) -> EventRequestDecision:
        """Conditionally deny the requested event request"""

        self.decision = EventRequestDecision(answer='denied_conditionally', reason=reason, condition=condition)

        return self.decision
