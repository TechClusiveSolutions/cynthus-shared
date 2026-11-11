"""Event Request Decision class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional

from .event_request_decision_answer import EventRequestDecisionAnswer
from .event_request_decision_condition import EventRequestDecisionCondition
from .event_request_decision_reason import EventRequestDecisionReason


class EventRequestDecision(BaseModel):
    """Represents the decision made on an event request"""

    answer: EventDecisionAnswer
    reason: EventDecisionReason
    condition: EventRequestDecisionCondition | None = None
    determined_by: Service
    determined_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
