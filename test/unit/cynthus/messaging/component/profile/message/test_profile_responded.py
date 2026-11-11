"""Tests for cynthus.messaging.component.profile.message.profile_responded."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.profile.message.profile_responded import ProfileRespondedMessage
from cynthus.messaging.component.profile.payload.profile_responded import ProfileRespondedPayload


def make_message():
    return ProfileRespondedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProfileRespondedPayload(operation='x', status=1),
    )


def test_event_type():
    assert make_message().event_type == 'public.profile.profile.responded'


def test_round_trips_through_json():
    message = make_message()

    assert ProfileRespondedMessage.model_validate_json(message.model_dump_json()) == message
