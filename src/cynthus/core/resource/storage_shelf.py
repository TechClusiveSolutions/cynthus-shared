"""Storage Shelf resource model class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .workspace_resource import WorkspaceResource


class StorageShelf(WorkspaceResource):
    """Represents a storage shelf resource"""

    has_lock: bool = Field(default=False)
    temperature_high: float = Field(description='high operating temperature')
    temperature_low: float = Field(description='low operating temperature')
    temperature_average: float = Field(description='average operating temperature')
    temperature_unit: str = Field(description='unit of measure for operating temperatures')
    x_slots: int = Field(default=1, description='number of positions on the X axis')
    y_slots: int = Field(default=1, description='number of positions on the Y axis')
    z_slots: int = Field(default=1, description='number of positions on the Z axis')
