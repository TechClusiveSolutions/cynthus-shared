"""Inventory Location Created Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InventoryLocationCreatedData(BaseModel):
    """The data of an inventory location created event"""

    model_config = ConfigDict(extra='forbid')

    location_id: str
    name: str
    type: str
