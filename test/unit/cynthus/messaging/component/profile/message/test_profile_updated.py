"""Tests for cynthus.messaging.component.profile.message.profile_updated."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.profile.message.profile_updated import ProfileUpdatedMessage
from cynthus.messaging.component.profile.payload.profile_updated import ProfileUpdatedPayload


def make_message():
    return ProfileUpdatedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProfileUpdatedPayload(profile_id='x', user_id='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.profile.profile.updated'


def test_round_trips_through_json():
    message = make_message()

    assert ProfileUpdatedMessage.model_validate_json(message.model_dump_json()) == message
