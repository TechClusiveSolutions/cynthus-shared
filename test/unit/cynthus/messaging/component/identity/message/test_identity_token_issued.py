"""Tests for cynthus.messaging.component.identity.message.identity_token_issued."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.identity.message.identity_token_issued import IdentityTokenIssuedMessage
from cynthus.messaging.component.identity.payload.identity_token_issued import IdentityTokenIssuedPayload


def make_message():
    return IdentityTokenIssuedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=IdentityTokenIssuedPayload(user_id='x', token_id='x', key_id='x', expires_in=1),
    )


def test_event_type():
    assert make_message().event_type == 'audit.identity.token.issued'


def test_round_trips_through_json():
    message = make_message()

    assert IdentityTokenIssuedMessage.model_validate_json(message.model_dump_json()) == message
