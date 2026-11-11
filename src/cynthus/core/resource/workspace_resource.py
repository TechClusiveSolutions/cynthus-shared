"""Workspace Resource model class for the Cynthus project"""

from __future__ import annotations

from .resource import Resource

from ..system import Workspace


class WorkspaceResource(Resource):
    """Represents a resource that belongs to a workspace"""

    workspace: Workspace
