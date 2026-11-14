"""Inventory Item Removed signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class InventoryItemRemovedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.item.removed signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    item_id: str = Field(..., description='The identifier of the item')
    shelf_id: str = Field(..., description='The identifier of the shelf')
    location_id: str = Field(..., description='The identifier of the location')
