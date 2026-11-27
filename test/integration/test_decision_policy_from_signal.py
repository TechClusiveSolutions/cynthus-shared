"""A signal request is authenticated, wrapped as an event request and decided, ending at the event request response"""

import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from cynthus.core.event import EventAction, EventRequest, EventRequestDecisionAnswer, SignalEvent
from cynthus.messaging.subscriber import ReceivedSignal
from cynthus.security import NO_WORKSPACE, TokenError, TokenIssuer, TokenVerifier
from cynthus.service import DecisionPolicy, Forbidden, SignalAccess

NOW = datetime(2026, 11, 27, 9, 30, tzinfo=timezone.utc)
PERMISSION = 'partner:read'
PEM = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
)
ISSUER = TokenIssuer(PEM, 'cynthus-auth', 'cynthus', ttl_seconds=300)


class Keys:
    def get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=ISSUER._private_key.public_key())


def received(identity, permissions=(PERMISSION,), owner=False):
    token = ISSUER.issue(**identity, permissions=list(permissions), owner=owner)

    return ReceivedSignal(event_type='public.partner.list.requested', body='{}',
                          properties={'authorization': f'Bearer {token}'})


def signal_of(identity):
    return SimpleNamespace(
        event_id=uuid.uuid4(), event_type='public.partner.list.requested', organization_id=identity['organization_id'],
        workspace_id=identity['workspace_id'], actor_id=identity['subject'],
    )


def identity():
    return {'subject': uuid.uuid4(), 'organization_id': uuid.uuid4(), 'workspace_id': uuid.uuid4()}


def access():
    return SignalAccess(TokenVerifier('http://auth.test/jwks', key_client=Keys()))


async def decide(who, resource_tenant_id, permissions=(PERMISSION,), owner=False):
    claims = await access().authenticate(received(who, permissions, owner), signal_of(who))
    event = SignalEvent(tenant_id=claims.tenant_id, workspace_id=claims.workspace_id, actor_id=claims.subject,
                        action=EventAction.RETRIEVED, data={})
    request = EventRequest(event=event, requestor=claims.subject)

    return DecisionPolicy(determined_by=uuid.uuid4(), clock=lambda: NOW).decide(
        request, claims, permission=PERMISSION, resource_tenant_id=resource_tenant_id
    )


@pytest.mark.asyncio
async def test_a_member_reading_its_own_tenant_is_access_permitted():
    who = identity()

    response = await decide(who, who['organization_id'])

    assert response.request.requestor_id == who['subject']
    assert response.decision.answer_reason == 'access_permitted' and response.in_effect is True


@pytest.mark.asyncio
async def test_an_owner_reading_its_own_tenant_is_permitted():
    who = identity()

    response = await decide(who, who['organization_id'], owner=True)

    assert response.decision.answer_reason == 'permitted' and response.in_effect is True


@pytest.mark.asyncio
async def test_a_platform_resource_is_access_permitted():
    assert (await decide(identity(), None)).decision.answer_reason == 'access_permitted'


@pytest.mark.asyncio
async def test_another_tenant_waits_for_an_approval():
    response = await decide(identity(), uuid.uuid4())

    assert response.decision.answer == EventRequestDecisionAnswer.APPROVED_CONDITIONALLY
    assert response.decision.conditions[0].expires_at == NOW + timedelta(days=5)
    assert response.in_effect is False


@pytest.mark.asyncio
async def test_a_genuine_token_without_the_permission_becomes_a_denied_decision_not_an_error():
    who = identity()

    response = await decide(who, who['organization_id'], permissions=())

    assert response.decision.answer == EventRequestDecisionAnswer.DENIED
    assert response.decision.answer_reason == 'insufficient_privileges' and response.in_effect is False


@pytest.mark.asyncio
async def test_a_token_for_another_actor_never_reaches_the_policy():
    who = identity()

    with pytest.raises(TokenError, match='does not match'):
        await access().authenticate(received(dict(who, subject=uuid.uuid4())), signal_of(who))


@pytest.mark.asyncio
async def test_a_person_without_a_workspace_never_reaches_the_policy():
    who = {**identity(), 'workspace_id': NO_WORKSPACE}

    with pytest.raises(Forbidden, match='workspace_required'):
        await access().authenticate(received(who), signal_of(who))
