"""StorageLocation resource model class for the Cynthus project"""

from __future__ import annotations

from pydantic import Field

from .storage_location_type import StorageLocationType
from .workspace_resource import WorkspaceResource


class StorageLocation(WorkspaceResource):
    """Represents a storage location resource"""

    type: StorageLocationType
    is_default: bool = Field(default=False, description='The workspace\'s default location (at most one is live)')
