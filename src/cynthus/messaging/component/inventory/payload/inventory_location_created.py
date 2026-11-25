"""Inventory Location Created signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class InventoryLocationCreatedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.location.created signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    location_id: str = Field(..., description='The identifier of the location')
    name: str = Field(..., description='The name of the location')
    type: str = Field(..., description='The kind of storage space, for example ambient, fridge or freezer')
