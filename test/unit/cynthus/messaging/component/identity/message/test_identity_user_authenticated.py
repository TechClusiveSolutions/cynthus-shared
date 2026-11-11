"""Tests for cynthus.messaging.component.identity.message.identity_user_authenticated."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.identity.message.identity_user_authenticated import IdentityUserAuthenticatedMessage
from cynthus.messaging.component.identity.payload.identity_user_authenticated import IdentityUserAuthenticatedPayload


def make_message():
    return IdentityUserAuthenticatedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=IdentityUserAuthenticatedPayload(user_id='x', username='x'),
    )


def test_event_type():
    assert make_message().event_type == 'audit.identity.user.authenticated'


def test_round_trips_through_json():
    message = make_message()

    assert IdentityUserAuthenticatedMessage.model_validate_json(message.model_dump_json()) == message
