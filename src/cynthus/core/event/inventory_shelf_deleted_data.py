"""Inventory Shelf Deleted Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InventoryShelfDeletedData(BaseModel):
    """The data of an inventory shelf deleted event"""

    model_config = ConfigDict(extra='forbid')

    shelf_id: str
    location_id: str
