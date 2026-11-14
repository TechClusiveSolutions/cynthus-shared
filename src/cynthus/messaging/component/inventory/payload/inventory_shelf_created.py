"""Inventory Shelf Created signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class InventoryShelfCreatedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.shelf.created signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    shelf_id: str = Field(..., description='The identifier of the shelf')
    location_id: str = Field(..., description='The identifier of the location')
    name: str = Field(..., description='The name of the shelf')
    position: int = Field(default=0, description='The position of the shelf within its location')
