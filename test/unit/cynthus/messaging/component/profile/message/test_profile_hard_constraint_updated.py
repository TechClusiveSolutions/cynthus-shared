"""Tests for cynthus.messaging.component.profile.message.profile_hard_constraint_updated."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.profile.message.profile_hard_constraint_updated import (
    ProfileHardConstraintUpdatedMessage,
)
from cynthus.messaging.component.profile.payload.profile_hard_constraint_updated import (
    ProfileHardConstraintUpdatedPayload,
)


def make_message():
    return ProfileHardConstraintUpdatedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ProfileHardConstraintUpdatedPayload(user_id='x', profile_id='x', kind='x'),
    )


def test_event_type():
    assert make_message().event_type == 'audit.profile.hard_constraint.updated'


def test_round_trips_through_json():
    message = make_message()

    assert ProfileHardConstraintUpdatedMessage.model_validate_json(message.model_dump_json()) == message
