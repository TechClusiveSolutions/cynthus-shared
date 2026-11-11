"""Tests for cynthus.messaging.component.profile.message.profile_created."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.profile.message.profile_created import ProfileCreatedMessage
from cynthus.messaging.component.profile.payload.profile_created import ProfileCreatedPayload


def make_message():
    return ProfileCreatedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProfileCreatedPayload(profile_id='x', user_id='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.profile.profile.created'


def test_round_trips_through_json():
    message = make_message()

    assert ProfileCreatedMessage.model_validate_json(message.model_dump_json()) == message
