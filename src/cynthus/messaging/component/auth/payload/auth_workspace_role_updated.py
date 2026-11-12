"""Auth Workspace Role Updated signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class AuthWorkspaceRoleUpdatedPayload(SignalPayload):
    """Represents the payload part of a public.auth.workspace_role.updated signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    workspace_role_id: str = Field(..., description='The identifier of the workspace role')
    user_id: str = Field(..., description='The identifier of the person who holds, or asked for, the role')
    role: str = Field(..., description='The role name: viewer, contributor, manager, admin or super_admin')
    status: str = Field(..., description='Where the role stands: pending, active or revoked')
    previous_status: str | None = Field(default=None, description='Where the role stood before this change')
