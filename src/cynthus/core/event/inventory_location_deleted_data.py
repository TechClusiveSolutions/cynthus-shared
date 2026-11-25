"""Inventory Location Deleted Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InventoryLocationDeletedData(BaseModel):
    """The data of an inventory location deleted event"""

    model_config = ConfigDict(extra='forbid')

    location_id: str
