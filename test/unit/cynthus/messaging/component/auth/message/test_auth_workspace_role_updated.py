"""Tests for cynthus.messaging.component.auth.message.auth_workspace_role_updated."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.auth.message.auth_workspace_role_updated import AuthWorkspaceRoleUpdatedMessage
from cynthus.messaging.component.auth.payload.auth_workspace_role_updated import AuthWorkspaceRoleUpdatedPayload


def make_message():
    return AuthWorkspaceRoleUpdatedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=AuthWorkspaceRoleUpdatedPayload(workspace_role_id='r', user_id='u', role='viewer', status='pending'),
    )


def test_event_type():
    assert make_message().event_type == 'public.auth.workspace_role.updated'


def test_round_trips_through_json():
    message = make_message()

    assert AuthWorkspaceRoleUpdatedMessage.model_validate_json(message.model_dump_json()) == message
