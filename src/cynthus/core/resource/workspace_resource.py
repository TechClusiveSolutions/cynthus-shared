"""Workspace Resource model class for the Cynthus project"""

from __future__ import annotations

from ..system import Workspace
from .resource import Resource


class WorkspaceResource(Resource):
    """Represents a resource that belongs to a workspace"""

    workspace: Workspace
