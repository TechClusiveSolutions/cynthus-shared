"""Auth Workspace Role Updated signal message for the Cynthus project"""

from ....common import PublicAuthWorkspaceRoleUpdatedSignal, SignalMessage
from ..payload import AuthWorkspaceRoleUpdatedPayload


class AuthWorkspaceRoleUpdatedMessage(SignalMessage[AuthWorkspaceRoleUpdatedPayload]):
    """
        Represents an auth workspace role updated signal message

        Emitted by: `cynthus-auth` when a request is answered, or a role is revoked or expires.
        Functional Purpose: Lets `cynthus-audit` record the answer, and services drop access that was revoked or has expired.
    """

    event_type: str = PublicAuthWorkspaceRoleUpdatedSignal.name
