"""Decision Condition class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .decision_condition_status import DecisionConditionStatus
from .event_request_decision_answer import EventRequestDecisionAnswer


class DecisionCondition(BaseModel):
    """
        Something that must happen before a conditionally approved request takes effect (ADR-013)

        ``condition`` is the answer reason a reply must carry to meet it; the test is an exact match. A reply that denies
        the request fails the condition, and no reply leaves it open until ``expires_at``.
    """

    id_: UUID = Field(default_factory=uuid4)
    condition: str = Field(description='The answer reason a reply must carry, for example approval_granted')
    status: DecisionConditionStatus = DecisionConditionStatus.OPEN
    expires_at: datetime | None = Field(default=None, description='When an open condition expires; empty means it does not')
    satisfied_by: UUID | None = Field(default=None, description='The decision that answered it')
    satisfied_on: datetime | None = None

    @property
    def is_open(self) -> bool:
        return self.status == DecisionConditionStatus.OPEN

    @property
    def is_met(self) -> bool:
        """Satisfied, or waived: either lets the request take effect."""

        return self.status in (DecisionConditionStatus.SATISFIED, DecisionConditionStatus.WAIVED)

    def answer(self, reply) -> DecisionConditionStatus:
        """
            Settles an open condition with a reply (an ``EventRequestDecision``) and returns where it stands

            The reply meets the condition when its answer reason equals the condition exactly. Any other reply that denies the
            request fails it. A reply that does neither leaves it open. A condition already settled is not changed.
        """

        if not self.is_open:
            return self.status

        if reply.answer_reason == self.condition:
            self.status = DecisionConditionStatus.SATISFIED
            self.satisfied_by = reply.id_
            self.satisfied_on = reply.determined_on
        elif reply.answer in (EventRequestDecisionAnswer.DENIED, EventRequestDecisionAnswer.DENIED_CONDITIONALLY):
            self.status = DecisionConditionStatus.FAILED
            self.satisfied_by = reply.id_
            self.satisfied_on = reply.determined_on

        return self.status

    def expire(self, now: datetime | None = None) -> bool:
        """Marks an open condition expired once its time has passed; returns whether it did."""

        now = now or datetime.now(timezone.utc)

        if self.is_open and self.expires_at is not None and self.expires_at <= now:
            self.status = DecisionConditionStatus.EXPIRED

            return True

        return False

    def waive(self) -> None:
        if self.is_open:
            self.status = DecisionConditionStatus.WAIVED
