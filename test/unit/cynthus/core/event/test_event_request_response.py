"""Event request response unit tests for the Cynthus project"""

import pytest

from cynthus.core.event import (
    EventAction,
    EventRequestDecisionAnswer,
    EventRequestDecisionCondition,
    EventRequestDecisionReason,
    EventRequestResponse,
    SystemEvent,
)
from cynthus.core.resource import StorageLocation
from cynthus.core.service import InventoryService
from cynthus.core.system import System, Tenant, Workspace
from cynthus.core.user import User


@pytest.fixture
def response():
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)
    service = InventoryService()
    event = service.build_event(
        tenant=tenant, workspace=workspace, resource=location, action=EventAction.CREATED, user=user)

    return EventRequestResponse(request=service.build_event_request(event, user))


def test_a_new_response_has_no_decision_yet(response):
    assert response.decision is None


def test_approve(response):
    decision = response.approve(EventRequestDecisionReason.PERMITTED)

    assert decision is response.decision
    assert decision.answer == EventRequestDecisionAnswer.APPROVED
    assert decision.reason == EventRequestDecisionReason.PERMITTED
    assert decision.condition is None
    assert decision.determined_by is None


def test_deny_names_the_service_that_decided(response):
    service = InventoryService()

    decision = response.deny(EventRequestDecisionReason.INSUFFICIENT_PRIVILEGES, determined_by=service.id_)

    assert decision.answer == EventRequestDecisionAnswer.DENIED
    assert decision.determined_by == service.id_


@pytest.mark.parametrize('method, answer', [
    ('conditionally_approve', EventRequestDecisionAnswer.APPROVED_CONDITIONALLY),
    ('conditionally_deny', EventRequestDecisionAnswer.DENIED_CONDITIONALLY),
])
def test_a_conditional_answer_carries_its_condition(response, method, answer):
    decision = getattr(response, method)(
        EventRequestDecisionReason.AUTHORIZATION_GRANTED, EventRequestDecisionCondition.AUTHORIZATION_REQUIRED)

    assert decision.answer == answer
    assert decision.condition == EventRequestDecisionCondition.AUTHORIZATION_REQUIRED


def test_a_later_decision_replaces_the_earlier_one(response):
    response.deny(EventRequestDecisionReason.AUTHORIZATION_REJECTED)
    response.approve(EventRequestDecisionReason.AUTHORIZATION_GRANTED)

    assert response.decision.answer == EventRequestDecisionAnswer.APPROVED


def test_a_system_event_is_taken_by_the_system(response):
    event = response.request.event

    system_event = SystemEvent(
        tenant=event.tenant, workspace=event.workspace, resource=event.resource, action=EventAction.UPDATED, data={})

    assert system_event.system == System()
    assert system_event.service_id is None
