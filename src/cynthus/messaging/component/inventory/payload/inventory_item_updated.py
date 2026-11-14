"""Inventory Item Updated signal payload class for the Cynthus project"""

from datetime import date
from typing import Optional

from pydantic import Field

from ....common import SignalPayload


class InventoryItemUpdatedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.item.updated signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    item_id: str = Field(..., description='The identifier of the item')
    shelf_id: str = Field(..., description='The identifier of the shelf')
    location_id: str = Field(..., description='The identifier of the location')
    name: Optional[str] = Field(default=None, description='The new name, when it changed')
    quantity: Optional[float] = Field(default=None, description='The new quantity, when it changed')
    unit: Optional[str] = Field(default=None, description='The new unit, when it changed')
    low_threshold: Optional[float] = Field(default=None, description='The new low threshold, when it changed')
    expiry_date: Optional[date] = Field(default=None, description='The new expiry date, when it changed')
