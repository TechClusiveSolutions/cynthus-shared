"""Inventory Location Updated signal payload class for the Cynthus project"""

from typing import Optional

from pydantic import Field

from ....common import SignalPayload


class InventoryLocationUpdatedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.location.updated signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    location_id: str = Field(..., description='The identifier of the location')
    name: Optional[str] = Field(default=None, description='The new name, when it changed')
    type: Optional[str] = Field(default=None, description='The new storage type, when it changed')
    archived: Optional[bool] = Field(default=None, description='Whether the location is now archived, when that changed')
