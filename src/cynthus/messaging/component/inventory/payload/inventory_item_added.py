"""Inventory Item Added signal payload class for the Cynthus project"""

from datetime import date
from typing import Optional

from pydantic import Field

from ....common import SignalPayload


class InventoryItemAddedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.item.added signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    item_id: str = Field(..., description='The identifier of the item')
    shelf_id: str = Field(..., description='The identifier of the shelf')
    location_id: str = Field(..., description='The identifier of the location')
    name: str = Field(..., description='The name of the item')
    quantity: float = Field(..., description='The quantity on hand')
    unit: Optional[str] = Field(default=None, description='The unit of measure, for example gallon')
    low_threshold: Optional[float] = Field(default=None, description='The quantity below which the item counts as low')
    expiry_date: Optional[date] = Field(default=None, description='The date the item expires')
    barcode: Optional[str] = Field(default=None, description='The barcode of the item')
    catalog_item_id: Optional[str] = Field(default=None, description='The catalog entry the item was matched to')
