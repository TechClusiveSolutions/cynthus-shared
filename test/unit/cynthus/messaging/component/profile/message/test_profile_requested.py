"""Tests for cynthus.messaging.component.profile.message.profile_requested."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.profile.message.profile_requested import ProfileRequestedMessage
from cynthus.messaging.component.profile.payload.profile_requested import ProfileRequestedPayload


def make_message():
    return ProfileRequestedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProfileRequestedPayload(operation='get'),
    )


def test_event_type():
    assert make_message().event_type == 'public.profile.profile.requested'


def test_round_trips_through_json():
    message = make_message()

    assert ProfileRequestedMessage.model_validate_json(message.model_dump_json()) == message
