"""Tests for cynthus.messaging.component.identity.message.identity_access_granted."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.identity.message.identity_access_granted import IdentityAccessGrantedMessage
from cynthus.messaging.component.identity.payload.identity_access_granted import IdentityAccessGrantedPayload


def make_message():
    return IdentityAccessGrantedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=IdentityAccessGrantedPayload(user_id='x', permission='x', resource='x', method='x'),
    )


def test_event_type():
    assert make_message().event_type == 'audit.identity.access.granted'


def test_round_trips_through_json():
    message = make_message()

    assert IdentityAccessGrantedMessage.model_validate_json(message.model_dump_json()) == message
