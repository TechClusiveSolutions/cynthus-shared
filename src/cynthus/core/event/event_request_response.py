"""Event Request Response class for the Cynthus project"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field

from .decision_condition import DecisionCondition
from .event_request import EventRequest
from .event_request_answer_reason import EventRequestAnswerReason
from .event_request_decision import EventRequestDecision
from .event_request_decision_answer import EventRequestDecisionAnswer


class EventRequestResponse(BaseModel):
    """
        Represents the decisions made on an event request

        Decisions are only ever added (ADR-013). The latest one is the current answer; ``in_effect`` says whether the
        request has taken effect, which for a conditional approval means every condition is met.
    """

    request: EventRequest
    decisions: list[EventRequestDecision] = Field(default_factory=list)

    @property
    def decision(self) -> EventRequestDecision | None:
        """The latest decision, or None while the request is undecided."""

        return self.decisions[-1] if self.decisions else None

    @property
    def in_effect(self) -> bool:
        decision = self.decision

        if decision is None:
            return False

        if decision.answer == EventRequestDecisionAnswer.APPROVED:
            return True

        return decision.answer == EventRequestDecisionAnswer.APPROVED_CONDITIONALLY and all(
            condition.is_met for condition in decision.conditions
        )

    def approve(self, answer_reason: str, determined_by: UUID | None = None) -> EventRequestDecision:
        """Approve the requested event request"""

        return self._decide(EventRequestDecisionAnswer.APPROVED, answer_reason, (), determined_by)

    def conditionally_approve(
        self, answer_reason: str, conditions: Iterable[DecisionCondition | str], determined_by: UUID | None = None
    ) -> EventRequestDecision:
        """Approve once the conditions are met; a condition given as text is the answer reason a reply must carry."""

        return self._decide(EventRequestDecisionAnswer.APPROVED_CONDITIONALLY, answer_reason, conditions, determined_by)

    def deny(self, answer_reason: str, determined_by: UUID | None = None) -> EventRequestDecision:
        """Deny the requested event request"""

        return self._decide(EventRequestDecisionAnswer.DENIED, answer_reason, (), determined_by)

    def conditionally_deny(
        self, answer_reason: str, conditions: Iterable[DecisionCondition | str], determined_by: UUID | None = None
    ) -> EventRequestDecision:
        """Deny unless the conditions are met."""

        return self._decide(EventRequestDecisionAnswer.DENIED_CONDITIONALLY, answer_reason, conditions, determined_by)

    def settle(self, reply: EventRequestDecision) -> list[DecisionCondition]:
        """
            Answers the open conditions of the latest decision with the decision of a reply and returns them

            A condition is met by a reply whose answer reason equals it exactly; a reply that denies fails it.
        """

        decision = self.decision

        if decision is None:
            return []

        for condition in decision.conditions:
            condition.answer(reply)

        return decision.conditions

    def expire(self, now: datetime | None = None, determined_by: UUID | None = None) -> EventRequestDecision | None:
        """
            Expires open conditions whose time has passed

            When any condition expires, a decision is added that denies the request with the answer reason ``expired``. It
            is a recorded decision, not a deletion. Returns that decision, or None when nothing expired.
        """

        decision = self.decision

        if decision is None:
            return None

        now = now or datetime.now(timezone.utc)

        if not any([condition.expire(now) for condition in decision.conditions]):
            return None

        return self._decide(EventRequestDecisionAnswer.DENIED, EventRequestAnswerReason.EXPIRED.value, (), determined_by)

    def _decide(self, answer, answer_reason, conditions, determined_by) -> EventRequestDecision:
        decision = EventRequestDecision(
            answer=answer,
            answer_reason=getattr(answer_reason, 'value', answer_reason),
            conditions=[c if isinstance(c, DecisionCondition) else DecisionCondition(condition=c) for c in conditions],
            determined_by=determined_by,
        )
        self.decisions.append(decision)

        return decision
