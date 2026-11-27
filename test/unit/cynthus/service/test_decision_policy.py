"""DecisionPolicy class unit tests for the Cynthus project"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from cynthus.core.event import (
    EventAction,
    EventRequest,
    EventRequestAnswerReason,
    EventRequestDecisionAnswer,
    EventRequestResponse,
    SignalEvent,
)
from cynthus.security import TokenClaims
from cynthus.service import DecisionPolicy

NOW = datetime(2026, 11, 27, 9, 30, tzinfo=timezone.utc)
PERMISSION = 'partner:read'
TENANT = uuid4()
OTHER_TENANT = uuid4()
SERVICE = uuid4()


def claims(permissions=(PERMISSION,), owner=False, tenant=TENANT):
    return TokenClaims(
        subject=uuid4(), organization_id=tenant, workspace_id=uuid4(), permissions=list(permissions), owner=owner,
        issued_at=1, expires_at=2,
    )


def request(who=None):
    who = who or claims()
    event = SignalEvent(
        tenant_id=who.tenant_id, workspace_id=who.workspace_id, actor_id=who.subject, action=EventAction.RETRIEVED, data={}
    )

    return EventRequest(event=event, requestor=who.subject)


def policy(**fields):
    return DecisionPolicy(determined_by=SERVICE, clock=lambda: NOW, **fields)


def decide(who, resource_tenant_id=TENANT, **fields):
    return policy(**fields).decide(request(who), who, permission=PERMISSION, resource_tenant_id=resource_tenant_id)


def test_rule_1_missing_permission_is_denied():
    response = decide(claims(permissions=()))

    assert response.decision.answer == EventRequestDecisionAnswer.DENIED
    assert response.decision.answer_reason == 'insufficient_privileges'
    assert response.decision.conditions == []
    assert response.in_effect is False


@pytest.mark.parametrize('resource_tenant_id', [None, TENANT, OTHER_TENANT])
@pytest.mark.parametrize('owner', [False, True])
def test_rule_1_wins_over_every_other_rule(resource_tenant_id, owner):
    response = decide(claims(permissions=['other:read'], owner=owner), resource_tenant_id)

    assert response.decision.answer_reason == 'insufficient_privileges' and response.in_effect is False


@pytest.mark.parametrize('owner', [False, True])
def test_rule_2_a_platform_resource_is_approved_as_access_permitted(owner):
    response = decide(claims(owner=owner), resource_tenant_id=None)

    assert response.decision.answer == EventRequestDecisionAnswer.APPROVED
    assert response.decision.answer_reason == EventRequestAnswerReason.ACCESS_PERMITTED == 'access_permitted'
    assert response.decision.conditions == [] and response.in_effect is True


def test_the_resource_tenant_defaults_to_platform_owned():
    who = claims()

    response = policy().decide(request(who), who, permission=PERMISSION)

    assert response.decision.answer_reason == 'access_permitted' and response.in_effect is True


def test_rule_3_the_owner_of_the_same_tenant_is_permitted():
    response = decide(claims(owner=True))

    assert response.decision.answer == EventRequestDecisionAnswer.APPROVED
    assert response.decision.answer_reason == 'permitted'
    assert response.decision.conditions == [] and response.in_effect is True


def test_rule_4_a_member_of_the_same_tenant_is_access_permitted():
    response = decide(claims(owner=False))

    assert response.decision.answer == EventRequestDecisionAnswer.APPROVED
    assert response.decision.answer_reason == 'access_permitted'
    assert response.decision.conditions == [] and response.in_effect is True


@pytest.mark.parametrize('owner', [False, True])
def test_rule_5_another_tenant_needs_approval(owner):
    response = decide(claims(owner=owner), resource_tenant_id=OTHER_TENANT)
    decision = response.decision

    assert decision.answer == EventRequestDecisionAnswer.APPROVED_CONDITIONALLY
    assert decision.answer_reason == 'approval_required'
    assert [(c.condition, c.status.value, c.expires_at) for c in decision.conditions] == [
        ('approval_granted', 'open', NOW + timedelta(days=5))
    ]
    assert response.in_effect is False


def test_the_approval_expiry_can_be_set():
    response = decide(claims(), OTHER_TENANT, approval_expiry=timedelta(hours=1))

    assert response.decision.conditions[0].expires_at == NOW + timedelta(hours=1)


def test_a_zero_expiry_expires_at_the_clock_time():
    response = decide(claims(), OTHER_TENANT, approval_expiry=timedelta(0))

    assert response.decision.conditions[0].expires_at == NOW


def test_the_default_expiry_is_five_days():
    response = DecisionPolicy(clock=lambda: NOW).decide(
        request(), claims(), permission=PERMISSION, resource_tenant_id=OTHER_TENANT
    )

    assert response.decision.conditions[0].expires_at == NOW + timedelta(days=5)


def test_the_default_clock_is_the_current_utc_time():
    before = datetime.now(timezone.utc)
    response = DecisionPolicy().decide(request(), claims(), permission=PERMISSION, resource_tenant_id=OTHER_TENANT)
    after = datetime.now(timezone.utc)

    assert before + timedelta(days=5) <= response.decision.conditions[0].expires_at <= after + timedelta(days=5)


@pytest.mark.parametrize(
    'who, resource_tenant_id',
    [
        (claims(permissions=()), TENANT),
        (claims(), None),
        (claims(owner=True), TENANT),
        (claims(), TENANT),
        (claims(), OTHER_TENANT),
    ],
)
def test_determined_by_is_set_on_every_decision(who, resource_tenant_id):
    assert decide(who, resource_tenant_id).decision.determined_by == SERVICE


def test_determined_by_defaults_to_none():
    who = claims()

    assert DecisionPolicy().decide(request(who), who, permission=PERMISSION).decision.determined_by is None


@pytest.mark.parametrize('resource_tenant_id', [None, TENANT, OTHER_TENANT])
def test_a_fixed_clock_gives_equal_results(resource_tenant_id):
    who = claims()
    asked = request(who)

    first = policy().decide(asked, who, permission=PERMISSION, resource_tenant_id=resource_tenant_id).decision
    second = policy().decide(asked, who, permission=PERMISSION, resource_tenant_id=resource_tenant_id).decision
    skip = {'id_', 'determined_on', 'conditions'}

    assert first.model_dump(exclude=skip) == second.model_dump(exclude=skip)
    assert [(c.condition, c.status, c.expires_at) for c in first.conditions] == [
        (c.condition, c.status, c.expires_at) for c in second.conditions
    ]


def test_the_response_wraps_the_request_with_one_decision():
    who = claims()
    asked = request(who)

    response = policy().decide(asked, who, permission=PERMISSION, resource_tenant_id=TENANT)

    assert isinstance(response, EventRequestResponse)
    assert response.request is asked and len(response.decisions) == 1


def test_the_policy_changes_neither_the_request_nor_the_claims():
    who = claims(owner=True)
    asked = request(who)
    before_request, before_claims = asked.model_dump(), who.model_dump()

    policy().decide(asked, who, permission=PERMISSION, resource_tenant_id=OTHER_TENANT)

    assert asked.model_dump() == before_request and who.model_dump() == before_claims


def test_the_conditional_approval_takes_effect_once_the_approval_is_granted():
    who = claims()
    response = decide(who, OTHER_TENANT)
    reply = EventRequestResponse(request=request(who))
    answer = reply.approve(EventRequestAnswerReason.APPROVAL_GRANTED)

    response.settle(answer)

    assert response.in_effect is True


@pytest.mark.parametrize('permission', ['', 'partner:READ', 'partner'])
def test_a_permission_must_match_exactly(permission):
    who = claims()

    response = policy().decide(request(who), who, permission=permission, resource_tenant_id=TENANT)

    assert response.decision.answer_reason == 'insufficient_privileges'
