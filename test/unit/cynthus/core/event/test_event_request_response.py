"""Event request decisions, conditions and the access request walk-through (ADR-013)"""

# A fixture is used by naming it as a test argument, which ruff reads as redefining the import
# ruff: noqa: F811

from datetime import datetime, timedelta, timezone

import pytest

from cynthus.core.event import (
    DecisionCondition,
    DecisionConditionStatus,
    EventAction,
    EventRequest,
    EventRequestAnswerReason,
    EventRequestDecisionAnswer,
    EventRequestResponse,
    SystemEvent,
)
from cynthus.core.service import InventoryService
from cynthus.core.system import System
from cynthus.core.test.factory import EventRequestFactory, UserEventFactory
from cynthus.core.test.fixture import decision_condition, event_request_response  # noqa: F401

NOW = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)
GRANTED = EventRequestAnswerReason.APPROVAL_GRANTED.value
DENIED = EventRequestAnswerReason.APPROVAL_DENIED.value
REQUIRED = EventRequestAnswerReason.APPROVAL_REQUIRED.value


def reply_to(response, **fields):
    """A second request that answers `response`, as Jack's approval answers Jill's access request."""

    return EventRequestResponse(request=EventRequestFactory(in_reply_to=response.request.id_, **fields))


# ------------------------------------------------------------------ decisions
def test_a_new_response_has_no_decision_and_is_not_in_effect(event_request_response):
    assert event_request_response.decision is None and event_request_response.decisions == []
    assert event_request_response.in_effect is False


def test_approve_is_in_effect_at_once(event_request_response):
    decision = event_request_response.approve(EventRequestAnswerReason.PERMITTED)

    assert decision is event_request_response.decision
    assert decision.answer == EventRequestDecisionAnswer.APPROVED
    assert decision.answer_reason == 'permitted' == EventRequestAnswerReason.PERMITTED
    assert decision.conditions == [] and decision.determined_by is None
    assert event_request_response.in_effect is True


def test_deny_names_the_service_that_decided(event_request_response):
    service = InventoryService()

    decision = event_request_response.deny(EventRequestAnswerReason.INSUFFICIENT_PRIVILEGES, determined_by=service.id_)

    assert decision.answer == EventRequestDecisionAnswer.DENIED and decision.determined_by == service.id_
    assert event_request_response.in_effect is False


def test_a_decision_is_added_never_changed(event_request_response):
    first = event_request_response.deny(DENIED)
    snapshot = first.model_dump()

    second = event_request_response.approve(GRANTED)

    assert event_request_response.decisions == [first, second]
    assert first.model_dump() == snapshot
    assert event_request_response.decision is second and first.id_ != second.id_


def test_a_conditional_decision_carries_its_conditions(event_request_response):
    decision = event_request_response.conditionally_approve(
        REQUIRED, [DecisionCondition(condition=GRANTED, expires_at=NOW + timedelta(days=5))])

    assert decision.answer == EventRequestDecisionAnswer.APPROVED_CONDITIONALLY and decision.answer_reason == REQUIRED
    (condition,) = decision.conditions
    assert condition.condition == GRANTED and condition.status == DecisionConditionStatus.OPEN
    assert condition.expires_at == NOW + timedelta(days=5)


def test_a_condition_given_as_text_is_the_answer_reason_a_reply_must_carry(event_request_response):
    decision = event_request_response.conditionally_deny(EventRequestAnswerReason.INSUFFICIENT_PRIVILEGES, [GRANTED])

    assert decision.answer == EventRequestDecisionAnswer.DENIED_CONDITIONALLY
    assert [c.condition for c in decision.conditions] == [GRANTED]


def test_a_conditional_approval_is_not_in_effect_until_every_condition_is_met(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED, 'payment_method_linked'])

    assert event_request_response.in_effect is False

    event_request_response.decision.conditions[0].status = DecisionConditionStatus.SATISFIED

    assert event_request_response.in_effect is False

    event_request_response.decision.conditions[1].waive()

    assert event_request_response.in_effect is True


# ------------------------------------------------------------------ the exact match
def test_a_reply_whose_answer_reason_equals_the_condition_meets_it(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED])
    approval = reply_to(event_request_response).approve(GRANTED)

    (condition,) = event_request_response.settle(approval)

    assert condition.status == DecisionConditionStatus.SATISFIED
    assert condition.satisfied_by == approval.id_ and condition.satisfied_on == approval.determined_on
    assert event_request_response.in_effect is True


def test_a_reply_that_denies_does_not_match_and_fails_the_condition(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED])
    refusal = reply_to(event_request_response).deny(DENIED)

    (condition,) = event_request_response.settle(refusal)

    assert refusal.answer_reason != condition.condition
    assert condition.status == DecisionConditionStatus.FAILED and condition.satisfied_by == refusal.id_
    assert event_request_response.in_effect is False


def test_a_reply_that_neither_matches_nor_denies_leaves_the_condition_open(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED])
    other = reply_to(event_request_response).approve(EventRequestAnswerReason.PERMITTED)

    (condition,) = event_request_response.settle(other)

    assert condition.status == DecisionConditionStatus.OPEN


def test_the_match_is_exact_not_a_prefix_or_a_case_variant(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED])

    for near in ('approval_grant', 'approval_granted_', 'APPROVAL_GRANTED'):
        (condition,) = event_request_response.settle(reply_to(event_request_response).approve(near))

        assert condition.status == DecisionConditionStatus.OPEN


def test_a_condition_that_is_settled_is_not_changed_by_a_later_reply(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED])
    first = reply_to(event_request_response).approve(GRANTED)
    event_request_response.settle(first)

    (condition,) = event_request_response.settle(reply_to(event_request_response).deny(DENIED))

    assert condition.status == DecisionConditionStatus.SATISFIED and condition.satisfied_by == first.id_


def test_each_condition_is_answered_by_its_own_reason(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED, 'payment_method_linked'])

    conditions = event_request_response.settle(reply_to(event_request_response).approve('payment_method_linked'))

    assert [c.status for c in conditions] == [DecisionConditionStatus.OPEN, DecisionConditionStatus.SATISFIED]


def test_settling_an_undecided_request_does_nothing(event_request_response):
    assert event_request_response.settle(reply_to(event_request_response).approve(GRANTED)) == []


# ------------------------------------------------------------------ expiry
def test_a_condition_past_its_time_expires_and_the_request_is_denied_with_a_recorded_decision(event_request_response):
    service = InventoryService()
    event_request_response.conditionally_approve(
        REQUIRED, [DecisionCondition(condition=GRANTED, expires_at=NOW + timedelta(days=5))])

    assert event_request_response.expire(NOW + timedelta(days=4)) is None

    expired = event_request_response.expire(NOW + timedelta(days=5), determined_by=service.id_)

    assert expired is event_request_response.decision
    assert expired.answer == EventRequestDecisionAnswer.DENIED and expired.answer_reason == 'expired'
    assert expired.determined_by == service.id_
    assert len(event_request_response.decisions) == 2  # the conditional decision is still there
    assert event_request_response.decisions[0].conditions[0].status == DecisionConditionStatus.EXPIRED
    assert event_request_response.in_effect is False


def test_a_condition_without_a_time_never_expires(event_request_response):
    event_request_response.conditionally_approve(REQUIRED, [GRANTED])

    assert event_request_response.expire(NOW + timedelta(days=3650)) is None
    assert event_request_response.decision.conditions[0].is_open


def test_a_settled_condition_does_not_expire(event_request_response):
    event_request_response.conditionally_approve(
        REQUIRED, [DecisionCondition(condition=GRANTED, expires_at=NOW + timedelta(days=5))])
    event_request_response.settle(reply_to(event_request_response).approve(GRANTED))

    assert event_request_response.expire(NOW + timedelta(days=30)) is None


def test_expiring_an_undecided_request_does_nothing(event_request_response):
    assert event_request_response.expire(NOW) is None


# ------------------------------------------------------------------ the walk-through of the ADR
def test_jill_asks_for_access_to_jacks_workspace_and_jack_approves():
    created = UserEventFactory(action=EventAction.CREATED)
    jill = created.user

    access = EventRequestResponse(request=EventRequest(event=created, requestor=jill))
    conditional = access.conditionally_approve(
        EventRequestAnswerReason.APPROVAL_REQUIRED,
        [DecisionCondition(condition=EventRequestAnswerReason.APPROVAL_GRANTED.value, expires_at=NOW + timedelta(days=5))])

    assert conditional.answer_reason == 'approval_required' and access.in_effect is False

    approval = EventRequestResponse(request=EventRequest(
        event=UserEventFactory(action=EventAction.UPDATED), requestor=jill, in_reply_to=access.request.id_))
    approval.approve(EventRequestAnswerReason.APPROVAL_GRANTED)
    access.settle(approval.decision)

    assert approval.request.in_reply_to == access.request.id_
    assert access.decisions == [conditional] and conditional.conditions[0].status == DecisionConditionStatus.SATISFIED
    assert access.in_effect is True


def test_a_system_event_is_taken_by_the_system(event_request_response):
    event = event_request_response.request.event

    system_event = SystemEvent(
        tenant=event.tenant, workspace=event.workspace, resource=event.resource, action=EventAction.UPDATED, data={})

    assert system_event.system == System()
    assert system_event.service_id is None


def test_a_condition_serializes_and_reads_back(decision_condition):
    assert DecisionCondition.model_validate_json(decision_condition.model_dump_json()) == decision_condition


@pytest.mark.parametrize('field', ['condition', 'status', 'expires_at', 'satisfied_by', 'satisfied_on'])
def test_a_condition_has_the_fields_of_the_adr(field):
    assert field in DecisionCondition.model_fields
