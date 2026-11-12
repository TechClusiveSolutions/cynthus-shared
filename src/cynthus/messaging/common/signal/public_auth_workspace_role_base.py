"""Public Auth Workspace Role Signal Base class for the Cynthus project"""

from .public_auth_base import PublicAuthSignalBase


class PublicAuthWorkspaceRoleSignalBase(PublicAuthSignalBase, abstract=True):
    """Intermediate base for all public auth workspace role signals. Sets the aggregate component."""

    aggregate = 'workspace_role'
