"""Inventory Location Deleted Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel


class InventoryLocationDeletedData(BaseModel):
    """The data of an inventory location deleted event"""

    location_id: str
