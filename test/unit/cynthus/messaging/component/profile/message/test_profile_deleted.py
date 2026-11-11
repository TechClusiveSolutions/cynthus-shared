"""Tests for cynthus.messaging.component.profile.message.profile_deleted."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.profile.message.profile_deleted import ProfileDeletedMessage
from cynthus.messaging.component.profile.payload.profile_deleted import ProfileDeletedPayload


def make_message():
    return ProfileDeletedMessage(
        lifecycle_action=LifecycleAction.DELETED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProfileDeletedPayload(profile_id='x', user_id='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.profile.profile.deleted'


def test_round_trips_through_json():
    message = make_message()

    assert ProfileDeletedMessage.model_validate_json(message.model_dump_json()) == message
