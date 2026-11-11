"""Tests for cynthus.messaging.component.identity.message.identity_user_rejected."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.identity.message.identity_user_rejected import IdentityUserRejectedMessage
from cynthus.messaging.component.identity.payload.identity_user_rejected import IdentityUserRejectedPayload


def make_message():
    return IdentityUserRejectedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=IdentityUserRejectedPayload(username='x'),
    )


def test_event_type():
    assert make_message().event_type == 'audit.identity.user.rejected'


def test_round_trips_through_json():
    message = make_message()

    assert IdentityUserRejectedMessage.model_validate_json(message.model_dump_json()) == message
