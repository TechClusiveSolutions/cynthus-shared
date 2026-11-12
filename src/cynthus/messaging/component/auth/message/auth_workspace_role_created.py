"""Auth Workspace Role Created signal message for the Cynthus project"""

from ....common import PublicAuthWorkspaceRoleCreatedSignal, SignalMessage
from ..payload import AuthWorkspaceRoleCreatedPayload


class AuthWorkspaceRoleCreatedMessage(SignalMessage[AuthWorkspaceRoleCreatedPayload]):
    """
        Represents an auth workspace role created signal message

        Emitted by: `cynthus-auth` when someone asks for a role in a workspace.
        Functional Purpose: Lets the person who owns the workspace, and `cynthus-audit`, see that a request for access was made.
    """

    event_type: str = PublicAuthWorkspaceRoleCreatedSignal.name
