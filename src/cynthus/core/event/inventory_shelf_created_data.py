"""Inventory Shelf Created Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InventoryShelfCreatedData(BaseModel):
    """The data of an inventory shelf created event"""

    model_config = ConfigDict(extra='forbid')

    shelf_id: str
    location_id: str
    name: str
    position: int = 0
