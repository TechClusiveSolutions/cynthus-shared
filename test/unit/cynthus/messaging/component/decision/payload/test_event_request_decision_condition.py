"""Tests for cynthus.messaging.component.decision.payload.event_request_decision_condition."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.decision.payload.event_request_decision_condition import (
    EventRequestDecisionConditionPayload,
)

EXPIRES = datetime(2026, 12, 1, 8, 0, tzinfo=timezone.utc)


def test_fields_are_exactly_the_contract():
    assert set(EventRequestDecisionConditionPayload.model_fields) == {'condition', 'status', 'expires_at'}


def test_expires_at_defaults_to_none():
    assert EventRequestDecisionConditionPayload(condition='approval_granted', status='open').expires_at is None


@pytest.mark.parametrize('name', ['condition', 'status'])
def test_required_fields(name):
    values = {'condition': 'approval_granted', 'status': 'open'}
    del values[name]

    with pytest.raises(ValidationError):
        EventRequestDecisionConditionPayload(**values)


def test_a_bad_expiry_is_rejected():
    with pytest.raises(ValidationError):
        EventRequestDecisionConditionPayload(condition='x', status='open', expires_at='tomorrow')


def test_a_non_string_condition_is_rejected():
    with pytest.raises(ValidationError):
        EventRequestDecisionConditionPayload(condition=['x'], status='open')


@pytest.mark.parametrize('expires_at', [EXPIRES, None])
def test_round_trips(expires_at):
    condition = EventRequestDecisionConditionPayload(condition='approval_granted', status='open', expires_at=expires_at)

    restored = EventRequestDecisionConditionPayload.model_validate_json(condition.model_dump_json())

    assert restored == condition
    assert restored.expires_at == expires_at
