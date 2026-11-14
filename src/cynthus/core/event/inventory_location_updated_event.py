"""Inventory Location Updated Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from .inventory_event import InventoryEvent
from .inventory_location_updated_data import InventoryLocationUpdatedData


class InventoryLocationUpdatedEvent(InventoryEvent):
    """Represents a change to an inventory location"""

    data_model: ClassVar[type[BaseModel] | None] = InventoryLocationUpdatedData
