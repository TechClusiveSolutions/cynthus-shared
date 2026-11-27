"""Tests for cynthus.messaging.component.decision.payload.event_request_decision."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.messaging.common.signal.payload import SignalPayload
from cynthus.messaging.component.decision.payload.event_request_decision import EventRequestDecisionPayload
from cynthus.messaging.component.decision.payload.event_request_decision_condition import (
    EventRequestDecisionConditionPayload,
)

FIELDS = {
    'schema_version', 'event_request_id', 'in_reply_to', 'requested_event_type', 'requested_action', 'requestor_id',
    'answer', 'answer_reason', 'conditions', 'determined_by', 'determined_on',
}
DETERMINED = datetime(2026, 11, 27, 9, 0, tzinfo=timezone.utc)


def _values(**extra):
    return {
        'schema_version': 1, 'event_request_id': uuid4(), 'requested_event_type': 'partner_service_list_requested',
        'requested_action': 'retrieved', 'requestor_id': uuid4(), 'answer': 'approved',
        'answer_reason': 'approval_granted', 'determined_on': DETERMINED, **extra,
    }


def test_is_a_signal_payload():
    assert issubclass(EventRequestDecisionPayload, SignalPayload)


def test_has_the_contract_fields():
    assert FIELDS <= set(EventRequestDecisionPayload.model_fields)
    assert set(EventRequestDecisionPayload.model_fields) - FIELDS <= set(SignalPayload.model_fields)


def test_the_defaults():
    payload = EventRequestDecisionPayload(**_values())

    assert payload.schema_version == 1

    assert payload.in_reply_to is None
    assert payload.determined_by is None
    assert payload.conditions == []


@pytest.mark.parametrize('name', ['event_request_id', 'requested_event_type', 'requested_action',
                                  'requestor_id', 'answer', 'answer_reason', 'determined_on'])
def test_required_fields(name):
    values = _values()
    del values[name]

    with pytest.raises(ValidationError):
        EventRequestDecisionPayload(**values)


@pytest.mark.parametrize('name', ['event_request_id', 'requestor_id', 'in_reply_to', 'determined_by'])
def test_a_bad_id_is_rejected(name):
    with pytest.raises(ValidationError):
        EventRequestDecisionPayload(**_values(**{name: 'x'}))


def test_a_bad_determined_on_is_rejected():
    with pytest.raises(ValidationError):
        EventRequestDecisionPayload(**_values(determined_on='soon'))


def test_schema_version_must_be_at_least_one():
    with pytest.raises(ValidationError):
        EventRequestDecisionPayload(**_values(schema_version=0))


def test_conditions_must_be_a_list_of_conditions():
    with pytest.raises(ValidationError):
        EventRequestDecisionPayload(**_values(conditions=[{'condition': 'x'}]))
    with pytest.raises(ValidationError):
        EventRequestDecisionPayload(**_values(conditions='nope'))


def test_round_trips_without_conditions():
    payload = EventRequestDecisionPayload(**_values(in_reply_to=uuid4(), determined_by=uuid4()))

    restored = EventRequestDecisionPayload.model_validate_json(payload.model_dump_json())

    assert restored == payload
    assert restored.determined_on == DETERMINED


def test_round_trips_with_two_conditions():
    expires = datetime(2026, 12, 1, tzinfo=timezone.utc)
    conditions = [
        EventRequestDecisionConditionPayload(condition='approval_granted', status='open', expires_at=expires),
        EventRequestDecisionConditionPayload(condition='second', status='satisfied', expires_at=None),
    ]
    payload = EventRequestDecisionPayload(**_values(answer='approved_conditionally', conditions=conditions))

    restored = EventRequestDecisionPayload.model_validate_json(payload.model_dump_json())

    assert restored == payload
    assert all(isinstance(c, EventRequestDecisionConditionPayload) for c in restored.conditions)
    assert [(c.condition, c.status, c.expires_at) for c in restored.conditions] == [
        ('approval_granted', 'open', expires), ('second', 'satisfied', None),
    ]
