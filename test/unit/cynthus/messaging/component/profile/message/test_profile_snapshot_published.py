"""Tests for cynthus.messaging.component.profile.message.profile_snapshot_published."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.profile.message.profile_snapshot_published import ProfileSnapshotPublishedMessage
from cynthus.messaging.component.profile.payload.profile_snapshot_published import ProfileSnapshotPublishedPayload


def make_message():
    return ProfileSnapshotPublishedMessage(
        lifecycle_action=LifecycleAction.SNAPSHOT,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProfileSnapshotPublishedPayload(user_id='x', profile={'a': 1}),
    )


def test_event_type():
    assert make_message().event_type == 'public.profile.snapshot.published'


def test_round_trips_through_json():
    message = make_message()

    assert ProfileSnapshotPublishedMessage.model_validate_json(message.model_dump_json()) == message
