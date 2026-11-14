"""Inventory Location Created Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from .inventory_event import InventoryEvent
from .inventory_location_created_data import InventoryLocationCreatedData


class InventoryLocationCreatedEvent(InventoryEvent):
    """Represents the creation of an inventory location"""

    data_model: ClassVar[type[BaseModel] | None] = InventoryLocationCreatedData
