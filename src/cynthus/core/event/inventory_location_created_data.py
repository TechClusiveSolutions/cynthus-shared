"""Inventory Location Created Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel


class InventoryLocationCreatedData(BaseModel):
    """The data of an inventory location created event"""

    location_id: str
    name: str
    type: str
