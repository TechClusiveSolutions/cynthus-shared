"""Event Request Decision signal payload class for the Cynthus project"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from ....common import SignalPayload
from .event_request_decision_condition import EventRequestDecisionConditionPayload


class EventRequestDecisionPayload(SignalPayload):
    """Represents the payload part of the four public.decision.event_request.* signal messages"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    event_request_id: UUID = Field(..., description='The request that was decided')
    in_reply_to: Optional[UUID] = Field(default=None, description='The request the decided request answers')
    requested_event_type: str = Field(..., description='The event type of the request, for example partner_service_list_requested')
    requested_action: str = Field(..., description='The action the request asked for')
    requestor_id: UUID = Field(..., description='The user or system that made the request')
    answer: str = Field(..., description='approved, approved_conditionally, denied or denied_conditionally')
    answer_reason: str = Field(..., description='Why the answer is what it is, for example approval_required')
    conditions: list[EventRequestDecisionConditionPayload] = Field(
        default_factory=list, description='What a conditional answer waits for'
    )
    determined_by: Optional[UUID] = Field(default=None, description='The service that made the decision')
    determined_on: datetime = Field(..., description='When the decision was made')
