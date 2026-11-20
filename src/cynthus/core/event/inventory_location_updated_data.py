"""Inventory Location Updated Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class InventoryLocationUpdatedData(BaseModel):
    """The data of an inventory location updated event: the id, and only the fields that changed"""

    model_config = ConfigDict(extra='forbid')

    location_id: str
    name: str | None = None
    type: str | None = None
    archived: bool | None = None

    @model_validator(mode='after')
    def _something_changed(self) -> InventoryLocationUpdatedData:
        if self.name is None and self.type is None and self.archived is None:
            raise ValueError('A location update must change the name, the type or the archived flag')

        return self
