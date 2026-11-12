"""Tests for cynthus.messaging.component.auth.payload.auth_workspace_role_created."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.auth.payload.auth_workspace_role_created import AuthWorkspaceRoleCreatedPayload


def make_payload(**more):
    return AuthWorkspaceRoleCreatedPayload(workspace_role_id='r', user_id='u', role='viewer', status='pending', **more)


def test_required_fields_are_kept():
    payload = make_payload()

    assert payload.schema_version == 1
    assert (payload.workspace_role_id, payload.user_id, payload.role, payload.status) == ('r', 'u', 'viewer', 'pending')


def test_defaults():
    assert make_payload().metadata == {}


def test_the_role_is_required():
    with pytest.raises(ValidationError):
        AuthWorkspaceRoleCreatedPayload()
