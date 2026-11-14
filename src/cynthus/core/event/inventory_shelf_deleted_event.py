"""Inventory Shelf Deleted Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from .inventory_event import InventoryEvent
from .inventory_shelf_deleted_data import InventoryShelfDeletedData


class InventoryShelfDeletedEvent(InventoryEvent):
    """Represents the deletion of an inventory shelf"""

    data_model: ClassVar[type[BaseModel] | None] = InventoryShelfDeletedData
