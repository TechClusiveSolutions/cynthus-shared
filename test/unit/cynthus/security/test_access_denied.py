from fastapi import FastAPI
from fastapi.testclient import TestClient

from cynthus.security import AccessDenied, access_denied_handler


def _client(status_code):
    application = FastAPI()
    application.add_exception_handler(AccessDenied, access_denied_handler)

    @application.get('/')
    async def route():
        raise AccessDenied(status_code, 'nope')

    return TestClient(application)


def test_the_error_keeps_its_status_and_reason():
    error = AccessDenied(403, 'nope')

    assert (error.status_code, error.reason, str(error)) == (403, 'nope', 'nope')


def test_an_unauthenticated_caller_gets_401_with_a_bearer_challenge():
    response = _client(401).get('/')

    assert response.status_code == 401
    assert response.json() == {'error': 'nope'}
    assert response.headers['www-authenticate'] == 'Bearer'


def test_a_caller_without_the_permission_gets_403_and_no_challenge():
    response = _client(403).get('/')

    assert response.status_code == 403
    assert response.json() == {'error': 'nope'}
    assert 'www-authenticate' not in response.headers
