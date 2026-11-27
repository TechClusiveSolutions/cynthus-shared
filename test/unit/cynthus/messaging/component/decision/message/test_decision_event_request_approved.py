"""Tests for cynthus.messaging.component.decision.message.decision_event_request_approved (DecisionEventRequestApprovedMessage)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.common.signal.public_decision_event_request_approved import (
    PublicDecisionEventRequestApprovedSignal,
)
from cynthus.messaging.component.decision.message.decision_event_request_approved import (
    DecisionEventRequestApprovedMessage,
)
from cynthus.messaging.component.decision.payload import (
    EventRequestDecisionConditionPayload,
    EventRequestDecisionPayload,
)

SIGNAL = PublicDecisionEventRequestApprovedSignal
MESSAGE = DecisionEventRequestApprovedMessage


def _payload():
    return EventRequestDecisionPayload(
        schema_version=1, event_request_id=uuid4(), in_reply_to=uuid4(),
        requested_event_type='partner_service_list_requested', requested_action='retrieved', requestor_id=uuid4(),
        answer='approved_conditionally', answer_reason='approval_required', determined_by=uuid4(),
        determined_on=datetime(2026, 11, 27, 9, 0, tzinfo=timezone.utc),
        conditions=[EventRequestDecisionConditionPayload(
            condition='approval_granted', status='open', expires_at=datetime(2026, 12, 1, tzinfo=timezone.utc))],
    )


def _message(payload=None):
    return MESSAGE(
        lifecycle_action=LifecycleAction.CREATED, correlation_id=uuid4(), organization_id=uuid4(),
        workspace_id=uuid4(), actor_id=uuid4(), payload=payload or _payload(),
    )


def test_event_type_equals_the_signal_name():
    assert _message().event_type == SIGNAL.name


def test_payload_is_typed():
    assert isinstance(_message().payload, EventRequestDecisionPayload)


def test_an_invalid_payload_is_rejected():
    with pytest.raises(ValidationError):
        _message(payload={'answer': 'approved'})


def test_round_trips():
    message = _message()

    restored = MESSAGE.model_validate_json(message.model_dump_json())

    assert restored == message
    assert restored.event_type == SIGNAL.name
    assert restored.payload.conditions == message.payload.conditions
    assert restored.correlation_id == message.correlation_id
    assert restored.actor_id == message.actor_id
