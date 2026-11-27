"""Event Request Decision Data class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..system import System
from ..user import User
from .event_request import EventRequest
from .event_request_decision import EventRequestDecision
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

    @classmethod
    def from_decision(cls, request: EventRequest, decision: EventRequestDecision) -> EventRequestDecisionData:
        """The data of ``decision``, made on ``request``: what the decision event and the decision cache both carry"""

        requested = request.event
        requestor = request.requestor
        requestor_id = requestor.id_ if isinstance(requestor, (User, System)) else requestor

        return cls(
            event_request_id=request.id_,
            in_reply_to=request.in_reply_to,
            requested_event_type=requested.event_type,
            requested_action=requested.action.value,
            requestor_id=requestor_id,
            answer=decision.answer.value,
            answer_reason=decision.answer_reason,
            conditions=[
                {'condition': c.condition, 'status': c.status.value, 'expires_at': c.expires_at}
                for c in decision.conditions
            ],
            determined_by=decision.determined_by,
            determined_on=decision.determined_on,
        )
