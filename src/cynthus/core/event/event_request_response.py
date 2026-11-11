"""Event Request Response class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from .event_request import EventRequest
from .event_request_decision import EventRequestDecision
from .event_request_decision_answer import EventRequestDecisionAnswer
from .event_request_decision_condition import EventRequestDecisionCondition
from .event_request_decision_reason import EventRequestDecisionReason


class EventRequestResponse(BaseModel):
    """Represents the response to an event request"""

    request: EventRequest
    decision: EventRequestDecision | None = None

    def approve(self, reason: EventRequestDecisionReason, determined_by: UUID | None = None) -> EventRequestDecision:
        """Approve the requested event request"""

        return self._decide(EventRequestDecisionAnswer.APPROVED, reason, None, determined_by)

    def conditionally_approve(
        self, reason: EventRequestDecisionReason, condition: EventRequestDecisionCondition,
        determined_by: UUID | None = None,
    ) -> EventRequestDecision:
        """Conditionally approve the requested event request"""

        return self._decide(EventRequestDecisionAnswer.APPROVED_CONDITIONALLY, reason, condition, determined_by)

    def deny(self, reason: EventRequestDecisionReason, determined_by: UUID | None = None) -> EventRequestDecision:
        """Deny the requested event request"""

        return self._decide(EventRequestDecisionAnswer.DENIED, reason, None, determined_by)

    def conditionally_deny(
        self, reason: EventRequestDecisionReason, condition: EventRequestDecisionCondition,
        determined_by: UUID | None = None,
    ) -> EventRequestDecision:
        """Conditionally deny the requested event request"""

        return self._decide(EventRequestDecisionAnswer.DENIED_CONDITIONALLY, reason, condition, determined_by)

    def _decide(self, answer, reason, condition, determined_by) -> EventRequestDecision:
        self.decision = EventRequestDecision(
            answer=answer, reason=reason, condition=condition, determined_by=determined_by
        )

        return self.decision
