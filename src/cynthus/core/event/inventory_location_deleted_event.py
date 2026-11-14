"""Inventory Location Deleted Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from .inventory_event import InventoryEvent
from .inventory_location_deleted_data import InventoryLocationDeletedData


class InventoryLocationDeletedEvent(InventoryEvent):
    """Represents the deletion of an inventory location"""

    data_model: ClassVar[type[BaseModel] | None] = InventoryLocationDeletedData
