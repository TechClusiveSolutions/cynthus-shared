"""Event Request Decision class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .decision_condition import DecisionCondition
from .event_request_decision_answer import EventRequestDecisionAnswer


class EventRequestDecision(BaseModel):
    """
        Represents a decision made on an event request

        A decision is a fact about one moment and is never changed (ADR-013). A later approval or a revocation is a new
        request with a new decision. ``answer_reason`` says why the answer is what it is; ``conditions`` are what a
        conditional answer waits for.
    """

    id_: UUID = Field(default_factory=uuid4)
    answer: EventRequestDecisionAnswer
    answer_reason: str = Field(description='Why the answer is what it is, for example approval_required')
    conditions: list[DecisionCondition] = Field(default_factory=list)
    determined_by: UUID | None = Field(default=None, description='The id of the service that made the decision')
    determined_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
