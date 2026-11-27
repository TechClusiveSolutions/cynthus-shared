"""SignalAccess.authenticate unit tests for the Cynthus project (the authorize tests are in test_signal_access.py)"""

import uuid
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from cynthus.security import NO_WORKSPACE, AccessRecorder, TokenError, TokenIssuer, TokenVerifier
from cynthus.service.forbidden import Forbidden
from cynthus.service.signal_access import SignalAccess

PEM = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
)
ISSUER = TokenIssuer(PEM, 'cynthus-auth', 'cynthus', ttl_seconds=300)
LIST = 'public.inventory.list.requested'


class Keys:
    def get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=ISSUER._private_key.public_key())


class Recorder(AccessRecorder):
    def __init__(self):
        self.events = []

    async def granted(self, claims, permission, resource, method):
        self.events.append(('granted', permission))

    async def rejected(self, reason, resource, method):
        self.events.append(('rejected', reason, resource, method))

    async def denied(self, claims, permission, resource, method):
        self.events.append(('denied', permission))


def access(recorder=None):
    return SignalAccess(TokenVerifier('http://auth.test/jwks', key_client=Keys()), recorder)


def who():
    return {'subject': uuid.uuid4(), 'organization_id': uuid.uuid4(), 'workspace_id': uuid.uuid4()}


def signal(identity):
    return SimpleNamespace(
        event_id=uuid.uuid4(), event_type=LIST, organization_id=identity['organization_id'],
        workspace_id=identity['workspace_id'], actor_id=identity['subject'],
    )


def message(identity, permissions=('inventory:read',)):
    header = f'Bearer {ISSUER.issue(**identity, permissions=list(permissions))}'

    return SimpleNamespace(application_properties={'authorization': header})


@pytest.mark.asyncio
async def test_a_genuine_matching_token_gives_its_claims():
    identity = who()

    claims = await access().authenticate(message(identity), signal(identity))

    assert (claims.subject, claims.organization_id, claims.workspace_id) == tuple(identity.values())
    assert claims.permissions == ['inventory:read']


@pytest.mark.asyncio
@pytest.mark.parametrize('permissions', [(), ('inventory:write',)])
async def test_a_token_that_lacks_a_permission_is_not_refused(permissions):
    identity = who()

    claims = await access().authenticate(message(identity, permissions=permissions), signal(identity))

    assert claims.subject == identity['subject']


@pytest.mark.asyncio
@pytest.mark.parametrize('properties', [None, {}, {'other': 'x'}])
async def test_a_signal_without_a_token_is_refused(properties):
    with pytest.raises(TokenError, match='missing'):
        await access().authenticate(SimpleNamespace(application_properties=properties), signal(who()))


@pytest.mark.asyncio
async def test_a_forged_token_is_refused():
    forged = SimpleNamespace(application_properties={'authorization': 'Bearer a.b.c'})

    with pytest.raises(TokenError, match='invalid token'):
        await access().authenticate(forged, signal(who()))


@pytest.mark.asyncio
@pytest.mark.parametrize('field', ['organization_id', 'workspace_id', 'subject'])
async def test_a_token_for_another_tenant_workspace_or_actor_is_refused(field):
    identity = who()

    with pytest.raises(TokenError, match='does not match'):
        await access().authenticate(message(dict(identity, **{field: uuid.uuid4()})), signal(identity))


@pytest.mark.asyncio
async def test_the_nil_workspace_is_refused_with_workspace_required():
    identity = {**who(), 'workspace_id': NO_WORKSPACE}

    with pytest.raises(Forbidden, match='workspace_required'):
        await access().authenticate(message(identity), signal(identity))


@pytest.mark.asyncio
async def test_a_refusal_is_recorded_as_rejected_like_authorize():
    identity = who()
    recorder = Recorder()
    nil = {**who(), 'workspace_id': NO_WORKSPACE}

    with pytest.raises(TokenError):
        await access(recorder).authenticate(SimpleNamespace(application_properties=None), signal(identity))

    with pytest.raises(TokenError):
        await access(recorder).authenticate(
            SimpleNamespace(application_properties={'authorization': 'Bearer a.b.c'}), signal(identity)
        )

    with pytest.raises(Forbidden):
        await access(recorder).authenticate(message(nil), signal(nil))

    with pytest.raises(TokenError):
        await access(recorder).authenticate(message(dict(identity, subject=uuid.uuid4())), signal(identity))

    assert recorder.events == [
        ('rejected', 'missing bearer token', LIST, 'SIGNAL'),
        ('rejected', 'invalid token', LIST, 'SIGNAL'),
        ('rejected', 'workspace_required', LIST, 'SIGNAL'),
        ('rejected', 'the token does not match the signal', LIST, 'SIGNAL'),
    ]


@pytest.mark.asyncio
async def test_a_success_records_neither_granted_nor_denied():
    identity = who()
    recorder = Recorder()

    await access(recorder).authenticate(message(identity), signal(identity))
    await access(recorder).authenticate(message(identity, permissions=()), signal(identity))

    assert recorder.events == []


@pytest.mark.asyncio
async def test_a_recorder_that_fails_never_changes_the_outcome():
    identity = who()

    class Broken(AccessRecorder):
        async def rejected(self, *arguments):
            raise RuntimeError('bus is down')

    with pytest.raises(TokenError, match='does not match'):
        await access(Broken()).authenticate(message(dict(identity, subject=uuid.uuid4())), signal(identity))
