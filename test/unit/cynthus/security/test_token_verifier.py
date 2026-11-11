import time
from unittest.mock import patch

import jwt
import pytest

from cynthus.security import TokenError, TokenIssuer, TokenVerifier
from cynthus.security import token_verifier as token_verifier_module


def test_a_valid_token_gives_its_claims(verifier, issuer, identity):
    claims = verifier.verify_sync(issuer.issue(**identity, roles=['admin'], permissions=['inventory:read']))

    assert claims.subject == identity['subject']
    assert claims.organization_id == identity['organization_id']
    assert claims.workspace_id == identity['workspace_id']
    assert claims.roles == ['admin'] and claims.has_permission('inventory:read')
    assert claims.expires_at > claims.issued_at


@pytest.mark.asyncio
async def test_verify_can_be_awaited(verifier, issuer, identity):
    assert (await verifier.verify(issuer.issue(**identity))).subject == identity['subject']


def test_an_expired_token_is_rejected(verifier, private_pem, identity):
    token = TokenIssuer(private_pem, 'cynthus-auth', 'cynthus', ttl_seconds=-120).issue(**identity)

    with pytest.raises(TokenError, match='expired'):
        verifier.verify_sync(token)


def test_a_token_signed_by_another_key_is_rejected(verifier, other_private_pem, identity):
    token = TokenIssuer(other_private_pem, 'cynthus-auth', 'cynthus').issue(**identity)

    with pytest.raises(TokenError, match='invalid'):
        verifier.verify_sync(token)


@pytest.mark.parametrize('issuer_name, audience', [('someone-else', 'cynthus'), ('cynthus-auth', 'other-service')])
def test_the_wrong_issuer_or_audience_is_rejected(verifier, private_pem, identity, issuer_name, audience):
    with pytest.raises(TokenError, match='invalid'):
        verifier.verify_sync(TokenIssuer(private_pem, issuer_name, audience).issue(**identity))


def test_garbage_is_rejected(verifier):
    with pytest.raises(TokenError):
        verifier.verify_sync('not-a-token')


def test_an_unsigned_token_is_rejected(verifier, identity):
    token = jwt.encode(
        {'iss': 'cynthus-auth', 'aud': 'cynthus', 'sub': str(identity['subject']),
         'iat': int(time.time()), 'exp': int(time.time()) + 60},
        key=None, algorithm='none',
    )

    with pytest.raises(TokenError):
        verifier.verify_sync(token)


def test_a_token_without_the_tenant_claims_is_rejected(verifier, issuer, key_client, private_pem, identity):
    now = int(time.time())
    token = jwt.encode(
        {'iss': 'cynthus-auth', 'aud': 'cynthus', 'sub': str(identity['subject']), 'iat': now, 'exp': now + 60},
        issuer._private_key, algorithm='RS256',
    )

    with pytest.raises(TokenError, match='missing required claims'):
        verifier.verify_sync(token)


def test_a_key_that_cannot_be_fetched_is_reported(verifier, issuer, key_client, identity):
    key_client.fail_with = jwt.PyJWKClientError('unreachable')

    with pytest.raises(TokenError, match='signing key'):
        verifier.verify_sync(issuer.issue(**identity))


def test_the_environment_supplies_the_settings(monkeypatch):
    monkeypatch.setenv('AUTH_JWKS_URL', 'http://auth.test/keys')
    monkeypatch.setenv('AUTH_ISSUER', 'me')
    monkeypatch.setenv('AUTH_AUDIENCE', 'you')

    verifier = TokenVerifier.from_environment()

    assert (verifier.jwks_url, verifier.issuer, verifier.audience) == ('http://auth.test/keys', 'me', 'you')


def test_the_defaults_point_at_the_auth_service(monkeypatch):
    for name in ('AUTH_JWKS_URL', 'AUTH_ISSUER', 'AUTH_AUDIENCE'):
        monkeypatch.delenv(name, raising=False)

    with patch.object(token_verifier_module.jwt, 'PyJWKClient') as client:
        verifier = TokenVerifier.from_environment()

    assert verifier.jwks_url == 'http://auth:8000/.well-known/jwks.json'
    assert (verifier.issuer, verifier.audience) == ('cynthus-auth', 'cynthus')
    client.assert_called_once()


def test_the_token_id_is_carried_into_the_claims(verifier, issuer, identity):
    issued = issuer.issue_token(**identity)

    assert verifier.verify_sync(issued.token).token_id == issued.token_id
