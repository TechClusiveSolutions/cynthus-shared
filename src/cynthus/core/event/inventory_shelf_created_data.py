"""Inventory Shelf Created Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel


class InventoryShelfCreatedData(BaseModel):
    """The data of an inventory shelf created event"""

    shelf_id: str
    location_id: str
    name: str
    position: int = 0
