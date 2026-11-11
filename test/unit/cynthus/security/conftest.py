import uuid
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from cynthus.security import TokenIssuer, TokenVerifier


def make_pem():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    return key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode('ascii')


@pytest.fixture(scope='session')
def private_pem():
    return make_pem()


@pytest.fixture(scope='session')
def other_private_pem():
    return make_pem()


@pytest.fixture
def issuer(private_pem):
    return TokenIssuer(private_pem, issuer='cynthus-auth', audience='cynthus', ttl_seconds=60)


class FakeKeyClient:
    """Stands in for PyJWKClient by handing back the issuer's public key."""

    def __init__(self, issuer):
        self.issuer = issuer
        self.fail_with = None

    def get_signing_key_from_jwt(self, token):
        if self.fail_with is not None:
            raise self.fail_with

        return SimpleNamespace(key=self.issuer._private_key.public_key())


@pytest.fixture
def key_client(issuer):
    return FakeKeyClient(issuer)


@pytest.fixture
def verifier(key_client):
    return TokenVerifier('http://auth.test/jwks', issuer='cynthus-auth', audience='cynthus', key_client=key_client)


@pytest.fixture
def identity():
    return {'subject': uuid.uuid4(), 'organization_id': uuid.uuid4(), 'workspace_id': uuid.uuid4()}
