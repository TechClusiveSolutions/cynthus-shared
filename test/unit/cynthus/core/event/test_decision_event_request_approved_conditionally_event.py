"""Tests for cynthus.core.event.decision_event_request_approved_conditionally_event (DecisionEventRequestApprovedConditionallyEvent)."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.core.event import EventAction, EventRequestDecisionData, EventRequestDecisionEvent
from cynthus.core.event.decision_event_request_approved_conditionally_event import (
    DecisionEventRequestApprovedConditionallyEvent as Direct,
)


def _data(answer='approved_conditionally'):
    return {
        'event_request_id': str(uuid4()), 'requested_event_type': 'partner_service_list_requested',
        'requested_action': 'retrieved', 'requestor_id': str(uuid4()), 'answer': answer,
        'answer_reason': 'approval_required', 'determined_on': '2026-11-27T09:00:00+00:00',
    }


def _make(action=EventAction.CREATED, answer='approved_conditionally'):
    return Direct(tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=action, data=_data(answer))


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.DecisionEventRequestApprovedConditionallyEvent is Direct


def test_is_a_decision_event():
    assert issubclass(Direct, EventRequestDecisionEvent)


def test_event_type():
    assert _make().event_type == 'decision_event_request_approved_conditionally'


def test_data_is_parsed():
    assert _make().parsed_data(EventRequestDecisionData).answer == 'approved_conditionally'


def test_only_created_is_allowed():
    assert Direct.actions == frozenset({EventAction.CREATED})


@pytest.mark.parametrize('action', [a for a in EventAction if a != EventAction.CREATED])
def test_any_other_action_is_refused(action):
    with pytest.raises(ValidationError):
        _make(action)


def test_the_matching_answer_is_accepted():
    assert _make(answer='approved_conditionally').parsed_data(EventRequestDecisionData).answer == 'approved_conditionally'


@pytest.mark.parametrize('other', ['approved', 'denied', 'denied_conditionally'])
def test_any_other_answer_is_refused(other):
    with pytest.raises(ValidationError):
        _make(answer=other)
