import uuid
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from cynthus.security import AccessRecorder, TokenError, TokenIssuer, TokenVerifier
from cynthus.service.signal_access import SignalAccess

PEM = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
)
ISSUER = TokenIssuer(PEM, 'cynthus-auth', 'cynthus', ttl_seconds=300)


class Keys:
    def get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=ISSUER._private_key.public_key())


def access():
    return SignalAccess(TokenVerifier('http://auth.test/jwks', key_client=Keys()))


def who():
    return {'subject': uuid.uuid4(), 'organization_id': uuid.uuid4(), 'workspace_id': uuid.uuid4()}


def signal(identity):
    return SimpleNamespace(
        event_id=uuid.uuid4(), event_type='public.inventory.list.requested',
        organization_id=identity['organization_id'], workspace_id=identity['workspace_id'],
        actor_id=identity['subject'],
    )


def message(identity, permissions=('inventory:read',), key='authorization', as_bytes=False):
    header = f'Bearer {ISSUER.issue(**identity, permissions=list(permissions))}'
    properties = {key.encode() if as_bytes else key: header.encode() if as_bytes else header}

    return SimpleNamespace(application_properties=properties)


@pytest.mark.asyncio
@pytest.mark.parametrize('key, as_bytes', [('authorization', False), ('Authorization', False), ('authorization', True)])
async def test_a_genuine_token_for_the_same_caller_is_accepted(key, as_bytes):
    identity = who()

    claims = await access().authorize(message(identity, key=key, as_bytes=as_bytes), signal(identity), 'inventory:read')

    assert claims.subject == identity['subject']


@pytest.mark.asyncio
@pytest.mark.parametrize('properties', [None, {}, {'other': 'x'}])
async def test_a_signal_without_a_token_is_refused(properties):
    identity = who()

    with pytest.raises(TokenError, match='missing'):
        await access().authorize(SimpleNamespace(application_properties=properties), signal(identity), 'inventory:read')


@pytest.mark.asyncio
async def test_a_message_object_without_properties_is_refused():
    with pytest.raises(TokenError, match='missing'):
        await access().authorize(SimpleNamespace(), signal(who()), 'inventory:read')


@pytest.mark.asyncio
async def test_a_forged_token_is_refused():
    identity = who()
    forged = SimpleNamespace(application_properties={'authorization': 'Bearer ' + 'a.b.c'})

    with pytest.raises(TokenError):
        await access().authorize(forged, signal(identity), 'inventory:read')


@pytest.mark.asyncio
async def test_a_token_without_the_permission_is_refused():
    identity = who()

    with pytest.raises(TokenError, match='does not grant inventory:read'):
        await access().authorize(message(identity, permissions=['inventory:write']), signal(identity), 'inventory:read')


@pytest.mark.asyncio
@pytest.mark.parametrize('field', ['organization_id', 'workspace_id', 'subject'])
async def test_a_token_for_another_caller_is_refused(field):
    identity = who()
    other = dict(identity, **{field: uuid.uuid4()})

    with pytest.raises(TokenError, match='does not match'):
        await access().authorize(message(other), signal(identity), 'inventory:read')


def test_the_verifier_is_built_from_the_environment_when_not_supplied(monkeypatch):
    monkeypatch.setenv('AUTH_JWKS_URL', 'http://auth.test/keys')

    verifier = SignalAccess().verifier

    assert verifier.jwks_url == 'http://auth.test/keys'
    assert SignalAccess(verifier).verifier is verifier


class Recorder(AccessRecorder):
    def __init__(self):
        self.events = []

    async def granted(self, claims, permission, resource, method):
        self.events.append(('granted', claims.subject, permission, resource, method))

    async def rejected(self, reason, resource, method):
        self.events.append(('rejected', reason, resource, method))

    async def denied(self, claims, permission, resource, method):
        self.events.append(('denied', claims.subject, permission, resource, method))


def recorded():
    recorder = Recorder()

    return SignalAccess(TokenVerifier('http://auth.test/jwks', key_client=Keys()), recorder), recorder


LIST = 'public.inventory.list.requested'


@pytest.mark.asyncio
async def test_a_genuine_request_is_recorded_as_granted():
    identity = who()
    access, recorder = recorded()

    await access.authorize(message(identity), signal(identity), 'inventory:read')

    assert recorder.events == [('granted', identity['subject'], 'inventory:read', LIST, 'SIGNAL')]


@pytest.mark.asyncio
async def test_a_missing_or_forged_token_is_recorded_as_rejected():
    identity = who()
    access, recorder = recorded()

    with pytest.raises(TokenError):
        await access.authorize(SimpleNamespace(application_properties=None), signal(identity), 'inventory:read')

    with pytest.raises(TokenError):
        await access.authorize(
            SimpleNamespace(application_properties={'authorization': 'Bearer a.b.c'}), signal(identity), 'inventory:read'
        )

    assert [event[:2] for event in recorder.events] == [('rejected', 'missing bearer token'), ('rejected', 'invalid token')]


@pytest.mark.asyncio
async def test_a_token_without_the_permission_is_recorded_as_denied():
    identity = who()
    access, recorder = recorded()

    with pytest.raises(TokenError):
        await access.authorize(message(identity, permissions=['inventory:write']), signal(identity), 'inventory:read')

    assert recorder.events == [('denied', identity['subject'], 'inventory:read', LIST, 'SIGNAL')]


@pytest.mark.asyncio
async def test_a_token_for_another_caller_is_recorded_as_rejected():
    identity = who()
    access, recorder = recorded()

    with pytest.raises(TokenError):
        await access.authorize(message(dict(identity, workspace_id=uuid.uuid4())), signal(identity), 'inventory:read')

    assert recorder.events == [('rejected', 'the token does not match the signal', LIST, 'SIGNAL')]


@pytest.mark.asyncio
async def test_a_recorder_that_fails_never_changes_the_decision():
    identity = who()

    class Broken(AccessRecorder):
        async def granted(self, *arguments):
            raise RuntimeError('bus is down')

    access = SignalAccess(TokenVerifier('http://auth.test/jwks', key_client=Keys()), Broken())

    assert (await access.authorize(message(identity), signal(identity), 'inventory:read')).subject == identity['subject']


@pytest.mark.asyncio
async def test_a_received_signal_carries_the_token_in_its_properties():
    from cynthus.messaging.subscriber import ReceivedSignal

    identity = who()
    raw = message(identity)
    received = ReceivedSignal(event_type='public.inventory.item.requested', body='{}',
                              properties=dict(raw.application_properties))

    claims = await access().authorize(received, signal(identity), 'inventory:read')

    assert claims.subject == identity['subject']


@pytest.mark.asyncio
async def test_a_received_signal_without_a_token_is_refused():
    from cynthus.messaging.subscriber import ReceivedSignal

    with pytest.raises(TokenError, match='missing'):
        await access().authorize(ReceivedSignal(event_type='a.b.c', body='{}'), signal(who()), 'inventory:read')


@pytest.mark.asyncio
async def test_a_token_with_the_nil_workspace_id_is_refused_even_when_the_signal_names_it():
    from cynthus.security import NO_WORKSPACE
    from cynthus.service.forbidden import Forbidden

    identity = {**who(), 'workspace_id': NO_WORKSPACE}

    with pytest.raises(Forbidden, match='workspace_required'):
        await access().authorize(message(identity), signal(identity), 'inventory:read')
