import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from cynthus.security import AccessDenied, AccessRecorder, RequirePermission, TokenIssuer, access_denied_handler


class Recorder(AccessRecorder):
    def __init__(self):
        self.events = []

    async def granted(self, claims, permission, resource, method):
        self.events.append(('granted', claims.subject, permission, resource, method))

    async def rejected(self, reason, resource, method):
        self.events.append(('rejected', reason, resource, method))

    async def denied(self, claims, permission, resource, method):
        self.events.append(('denied', claims.subject, permission, resource, method))


@pytest.fixture
def recorder():
    return Recorder()


@pytest.fixture
def application(verifier, recorder):
    application = FastAPI()
    application.add_exception_handler(AccessDenied, access_denied_handler)
    application.state.token_verifier = verifier
    application.state.access_recorder = recorder

    @application.get('/read')
    async def read(request: Request, claims=Depends(RequirePermission('inventory:read'))):
        return {'subject': str(claims.subject), 'dots': request.state.access_token.count('.')}

    return application


@pytest.fixture
def client(application):
    return TestClient(application)


def bearer(issuer, identity, permissions=('inventory:read',)):
    return {'Authorization': f'Bearer {issuer.issue(**identity, permissions=list(permissions))}'}


def test_a_token_with_the_permission_is_let_through_with_its_claims(client, issuer, identity, recorder):
    response = client.get('/read', headers=bearer(issuer, identity))

    assert response.status_code == 200
    assert response.json() == {'subject': str(identity['subject']), 'dots': 2}
    assert recorder.events == [('granted', identity['subject'], 'inventory:read', '/read', 'GET')]


def test_a_missing_header_is_401_and_recorded_as_rejected(client, recorder):
    response = client.get('/read')

    assert response.status_code == 401
    assert response.json() == {'error': 'missing bearer token'}
    assert response.headers['www-authenticate'] == 'Bearer'
    assert recorder.events == [('rejected', 'missing bearer token', '/read', 'GET')]


def test_another_scheme_is_401(client, recorder):
    assert client.get('/read', headers={'Authorization': 'Basic abc'}).status_code == 401
    assert recorder.events[0][:2] == ('rejected', 'malformed authorization header')


def test_a_token_signed_by_another_key_is_401(client, other_private_pem, identity, recorder):
    stranger = TokenIssuer(other_private_pem, 'cynthus-auth', 'cynthus')

    response = client.get('/read', headers=bearer(stranger, identity))

    assert response.status_code == 401
    assert response.json() == {'error': 'invalid token'}
    assert recorder.events[0][:2] == ('rejected', 'invalid token')


def test_an_expired_token_is_401(client, private_pem, identity):
    expired = TokenIssuer(private_pem, 'cynthus-auth', 'cynthus', ttl_seconds=-120)

    response = client.get('/read', headers=bearer(expired, identity))

    assert response.status_code == 401
    assert response.json() == {'error': 'token expired'}


def test_a_valid_token_without_the_permission_is_403_and_recorded_as_denied(client, issuer, identity, recorder):
    response = client.get('/read', headers=bearer(issuer, identity, permissions=['inventory:write']))

    assert response.status_code == 403
    assert response.json() == {'error': 'the token does not grant inventory:read'}
    assert 'www-authenticate' not in response.headers
    assert recorder.events == [('denied', identity['subject'], 'inventory:read', '/read', 'GET')]


def test_no_recorder_is_needed(application, issuer, identity):
    del application.state.access_recorder

    assert TestClient(application).get('/read', headers=bearer(issuer, identity)).status_code == 200


def test_a_recorder_that_fails_never_changes_the_outcome(application, issuer, identity):
    class Broken(AccessRecorder):
        async def granted(self, *arguments):
            raise RuntimeError('bus is down')

        async def rejected(self, *arguments):
            raise RuntimeError('bus is down')

    application.state.access_recorder = Broken()
    client = TestClient(application)

    assert client.get('/read', headers=bearer(issuer, identity)).status_code == 200
    assert client.get('/read').status_code == 401


@pytest.mark.asyncio
async def test_authorize_can_be_used_without_a_request(application, issuer, identity, recorder):
    permission = RequirePermission('inventory:read')
    token = issuer.issue(**identity, permissions=['inventory:read'])

    claims = await permission.authorize(application, token, '/ws/1', 'WEBSOCKET')

    assert claims.subject == identity['subject']
    assert recorder.events == [('granted', identity['subject'], 'inventory:read', '/ws/1', 'WEBSOCKET')]
