"""ApiError, Body, Fact, Facts, Forbidden, Identifier and Outcome: the small classes every service shares."""

import logging
import uuid
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel, Field

from cynthus.messaging.common import LifecycleAction
from cynthus.security import TokenClaims, TokenError
from cynthus.service import ApiError, Body, Fact, Facts, Forbidden, Identifier, Outcome


class Thing(BaseModel):
    name: str = Field(min_length=1)
    size: int | None = None


class FakeMessage:
    def __init__(self, **fields):
        self.fields = fields
        self.event_type = 'public.thing.created'


def test_an_api_error_keeps_its_status_and_message():
    error = ApiError(404, 'thing not found')

    assert (error.status_code, error.message, str(error)) == (404, 'thing not found', 'thing not found')


def test_invalid_input_is_a_422_naming_the_first_problem():
    with pytest.raises(ApiError) as caught:
        Body.validate(Thing, {'name': ''})

    assert caught.value.status_code == 422
    assert caught.value.message.startswith('name:')


def test_an_error_with_no_location_is_described_by_its_message():
    try:
        Thing.model_validate('not an object')
    except Exception as validation:
        error = ApiError.invalid(validation)

    assert error.status_code == 422 and not error.message.startswith(('.', ':'))


def test_valid_input_is_returned_as_the_schema():
    assert Body.validate(Thing, {'name': 'x', 'size': 2}) == Thing(name='x', size=2)


def test_changes_are_the_fields_that_were_sent_and_not_null():
    body = Thing.model_validate({'name': 'x', 'size': None})

    assert Body.changes(body) == {'name': 'x'}
    assert Body.changes(Thing.model_validate({'size': 3, 'name': 'y'})) == {'size': 3, 'name': 'y'}


def test_a_forbidden_error_is_a_token_error():
    error = Forbidden('the token does not grant x')

    assert isinstance(error, TokenError) and error.reason == 'the token does not grant x'


def test_an_identifier_is_read_from_text_or_a_uuid():
    value = uuid.uuid4()

    assert Identifier.parse(str(value), 'resource_id') == value
    assert Identifier.parse(value, 'resource_id') == value


@pytest.mark.parametrize('value', [None, ''])
def test_a_missing_identifier_is_a_422(value):
    with pytest.raises(ApiError) as caught:
        Identifier.parse(value, 'resource_id')

    assert (caught.value.status_code, caught.value.message) == (422, 'resource_id: is required')


def test_a_malformed_identifier_is_a_422():
    with pytest.raises(ApiError) as caught:
        Identifier.parse('nope', 'parent_id')

    assert (caught.value.status_code, caught.value.message) == (422, 'parent_id: is not a valid identifier')


def test_an_optional_identifier_may_be_absent():
    value = uuid.uuid4()

    assert Identifier.optional(None, 'x') is None and Identifier.optional('', 'x') is None
    assert Identifier.optional(str(value), 'x') == value

    with pytest.raises(ApiError):
        Identifier.optional('nope', 'x')


def test_an_outcome_defaults_to_nothing_to_report():
    outcome = Outcome(204)

    assert (outcome.status, outcome.result, outcome.error, outcome.facts) == (204, None, None, [])


def test_outcomes_do_not_share_their_facts():
    first, second = Outcome(200), Outcome(200)
    first.facts.append('x')

    assert second.facts == []


def test_a_fact_is_a_message_class_a_lifecycle_and_a_payload():
    fact = Fact(FakeMessage, LifecycleAction.CREATED, {'a': 1})

    assert (fact.message_class, fact.lifecycle, fact.payload) == (FakeMessage, LifecycleAction.CREATED, {'a': 1})


@pytest.fixture
def claims():
    return TokenClaims(
        subject=uuid.uuid4(), organization_id=uuid.uuid4(), workspace_id=uuid.uuid4(), issued_at=1, expires_at=2
    )


@pytest.mark.asyncio
async def test_a_fact_is_published_for_the_callers_tenant(claims):
    publisher = AsyncMock()

    await Facts.publish(publisher, claims, Fact(FakeMessage, LifecycleAction.UPDATED, 'payload'))

    (message,) = [call.args[0] for call in publisher.publish.await_args_list]
    assert message.fields['payload'] == 'payload' and message.fields['lifecycle_action'] is LifecycleAction.UPDATED
    assert (message.fields['organization_id'], message.fields['workspace_id'], message.fields['actor_id']) == (
        claims.organization_id, claims.workspace_id, claims.subject)
    assert isinstance(message.fields['correlation_id'], uuid.UUID)


@pytest.mark.asyncio
async def test_a_bus_failure_is_logged_and_not_raised(claims, caplog):
    publisher = AsyncMock()
    publisher.publish.side_effect = RuntimeError('bus is down')

    with caplog.at_level(logging.ERROR):
        await Facts.publish(publisher, claims, Fact(FakeMessage, LifecycleAction.CREATED, 'p'))

    assert 'Could not publish public.thing.created' in caplog.text
