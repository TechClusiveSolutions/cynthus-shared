"""Tests for cynthus.core.event.event_request_decision_data (EventRequestDecisionData)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.event_request_decision_data import EventRequestDecisionData

FIELDS = {
    'schema_version', 'event_request_id', 'in_reply_to', 'requested_event_type', 'requested_action', 'requestor_id',
    'answer', 'answer_reason', 'conditions', 'determined_by', 'determined_on',
}


def _values(**extra):
    return {
        'event_request_id': uuid4(), 'requested_event_type': 'partner_service_list_requested',
        'requested_action': 'retrieved', 'requestor_id': uuid4(), 'answer': 'approved',
        'answer_reason': 'approval_granted', 'determined_on': datetime(2026, 11, 27, 9, 0, tzinfo=timezone.utc),
        **extra,
    }


def test_is_a_pydantic_model():
    assert issubclass(EventRequestDecisionData, BaseModel)


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.EventRequestDecisionData is EventRequestDecisionData


def test_fields_are_exactly_the_contract():
    assert set(EventRequestDecisionData.model_fields) == FIELDS


def test_defaults():
    data = EventRequestDecisionData(**_values())

    assert data.schema_version == 1
    assert data.in_reply_to is None
    assert data.determined_by is None
    assert data.conditions == []


@pytest.mark.parametrize('name', ['event_request_id', 'requested_event_type', 'requested_action', 'requestor_id',
                                  'answer', 'answer_reason', 'determined_on'])
def test_required_fields(name):
    values = _values()
    del values[name]

    with pytest.raises(ValidationError):
        EventRequestDecisionData(**values)


@pytest.mark.parametrize('name', ['event_request_id', 'requestor_id', 'in_reply_to', 'determined_by'])
def test_ids_must_be_uuids(name):
    with pytest.raises(ValidationError):
        EventRequestDecisionData(**_values(**{name: 'nope'}))


def test_conditions_are_parsed_from_dicts():
    expires = datetime(2026, 12, 1, tzinfo=timezone.utc)
    values = _values(
        event_request_id=str(uuid4()), requestor_id=str(uuid4()), determined_on='2026-11-27T09:00:00+00:00',
        conditions=[
            {'condition': 'approval_granted', 'status': 'open', 'expires_at': expires.isoformat()},
            {'condition': 'other', 'status': 'satisfied', 'expires_at': None},
        ],
    )

    data = EventRequestDecisionData.model_validate(values)

    assert [c.condition for c in data.conditions] == ['approval_granted', 'other']
    assert data.conditions[0].expires_at == expires
    assert data.conditions[1].expires_at is None


def test_condition_with_a_non_string_status_is_refused():
    with pytest.raises(ValidationError):
        EventRequestDecisionData(**_values(conditions=[{'condition': 'x', 'status': 5, 'expires_at': None}]))


@pytest.mark.parametrize('bad', [0, -1])
def test_schema_version_must_be_at_least_one(bad):
    with pytest.raises(ValidationError):
        EventRequestDecisionData(**_values(schema_version=bad))


def test_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        EventRequestDecisionData(**_values(other=1))


def test_extra_is_forbidden_in_the_config():
    assert EventRequestDecisionData.model_config['extra'] == 'forbid'
