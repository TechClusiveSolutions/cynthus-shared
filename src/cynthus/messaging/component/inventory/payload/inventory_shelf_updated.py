"""Inventory Shelf Updated signal payload class for the Cynthus project"""

from typing import Optional

from pydantic import Field

from ....common import SignalPayload


class InventoryShelfUpdatedPayload(SignalPayload):
    """Represents the payload part of a public.inventory.shelf.updated signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    shelf_id: str = Field(..., description='The identifier of the shelf')
    location_id: str = Field(..., description='The identifier of the location')
    name: Optional[str] = Field(default=None, description='The new name, when it changed')
    position: Optional[int] = Field(default=None, description='The new position, when it changed')
