"""Public Auth Workspace Role Updated signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_auth_workspace_role_base import PublicAuthWorkspaceRoleSignalBase


class PublicAuthWorkspaceRoleUpdatedSignal(PublicAuthWorkspaceRoleSignalBase):
    """Concrete signal: public.auth.workspace_role.updated"""

    action = SignalActionType.UPDATED
