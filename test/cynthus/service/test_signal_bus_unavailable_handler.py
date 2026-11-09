"""Tests for cynthus.service.signal_bus_unavailable_handler (signal_bus_unavailable_handler)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from cynthus.messaging.publisher import SignalBusUnavailable
from cynthus.service import signal_bus_unavailable_handler
from cynthus.service.signal_bus_unavailable_handler import CODE, RETRY_AFTER_SECONDS


def _client(message='ConnectionsQuotaExceeded for namespace secret-namespace'):
    application = FastAPI()
    application.add_exception_handler(SignalBusUnavailable, signal_bus_unavailable_handler)

    @application.get('/')
    async def route():
        raise SignalBusUnavailable(message)

    return TestClient(application)


def test_a_request_that_needed_the_bus_gets_503_with_retry_after_and_a_code():
    response = _client().get('/')

    assert response.status_code == 503
    assert response.headers['retry-after'] == str(RETRY_AFTER_SECONDS)
    assert response.json()['code'] == CODE == 'service_unavailable'
    assert response.json()['error']


def test_the_text_of_the_error_behind_it_is_never_shown():
    response = _client().get('/')

    assert 'secret-namespace' not in response.text


def test_the_same_answer_can_be_built_by_a_service_that_has_no_exception_to_raise():
    from cynthus.service import unavailable_response

    response = unavailable_response()

    assert response.status_code == 503
    assert response.headers['retry-after'] == str(RETRY_AFTER_SECONDS)
    assert b'service_unavailable' in response.body
