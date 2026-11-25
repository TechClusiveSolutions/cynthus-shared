"""Inventory Shelf Updated Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class InventoryShelfUpdatedData(BaseModel):
    """The data of an inventory shelf updated event: the ids, and only the fields that changed"""

    model_config = ConfigDict(extra='forbid')

    shelf_id: str
    location_id: str
    name: str | None = None
    position: int | None = None

    @model_validator(mode='after')
    def _something_changed(self) -> InventoryShelfUpdatedData:
        if self.name is None and self.position is None:
            raise ValueError('A shelf update must change the name or the position')

        return self
