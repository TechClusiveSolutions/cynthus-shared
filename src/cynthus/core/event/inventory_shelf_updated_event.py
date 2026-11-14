"""Inventory Shelf Updated Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from .inventory_event import InventoryEvent
from .inventory_shelf_updated_data import InventoryShelfUpdatedData


class InventoryShelfUpdatedEvent(InventoryEvent):
    """Represents a change to an inventory shelf"""

    data_model: ClassVar[type[BaseModel] | None] = InventoryShelfUpdatedData
