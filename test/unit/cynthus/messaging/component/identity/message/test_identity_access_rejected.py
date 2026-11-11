"""Tests for cynthus.messaging.component.identity.message.identity_access_rejected."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.identity.message.identity_access_rejected import IdentityAccessRejectedMessage
from cynthus.messaging.component.identity.payload.identity_access_rejected import IdentityAccessRejectedPayload


def make_message():
    return IdentityAccessRejectedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=IdentityAccessRejectedPayload(reason='x', resource='x', method='x'),
    )


def test_event_type():
    assert make_message().event_type == 'audit.identity.access.rejected'


def test_round_trips_through_json():
    message = make_message()

    assert IdentityAccessRejectedMessage.model_validate_json(message.model_dump_json()) == message
