"""Tests for cynthus.messaging.component.auth.message.auth_workspace_role_created."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.auth.message.auth_workspace_role_created import AuthWorkspaceRoleCreatedMessage
from cynthus.messaging.component.auth.payload.auth_workspace_role_created import AuthWorkspaceRoleCreatedPayload


def make_message():
    return AuthWorkspaceRoleCreatedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=AuthWorkspaceRoleCreatedPayload(workspace_role_id='r', user_id='u', role='viewer', status='pending'),
    )


def test_event_type():
    assert make_message().event_type == 'public.auth.workspace_role.created'


def test_round_trips_through_json():
    message = make_message()

    assert AuthWorkspaceRoleCreatedMessage.model_validate_json(message.model_dump_json()) == message
