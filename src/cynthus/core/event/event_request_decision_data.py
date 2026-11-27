"""Event Request Decision Data class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .event_request_decision_condition_data import EventRequestDecisionConditionData


class EventRequestDecisionData(BaseModel):
    """The data of an event request decision event: the request that was decided and the decision itself"""

    model_config = ConfigDict(extra='forbid')

    schema_version: int = Field(1, ge=1)
    event_request_id: UUID
    in_reply_to: UUID | None = None
    requested_event_type: str
    requested_action: str
    requestor_id: UUID
    answer: str
    answer_reason: str
    conditions: list[EventRequestDecisionConditionData] = Field(default_factory=list)
    determined_by: UUID | None = None
    determined_on: datetime
