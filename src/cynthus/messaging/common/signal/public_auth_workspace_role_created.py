"""Public Auth Workspace Role Created signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_auth_workspace_role_base import PublicAuthWorkspaceRoleSignalBase


class PublicAuthWorkspaceRoleCreatedSignal(PublicAuthWorkspaceRoleSignalBase):
    """Concrete signal: public.auth.workspace_role.created"""

    action = SignalActionType.CREATED
