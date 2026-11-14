"""Inventory Location Deleted signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class InventoryLocationDeletedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.location.deleted signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    location_id: str = Field(..., description='The identifier of the location')
