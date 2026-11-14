"""Inventory Shelf Created Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from .inventory_event import InventoryEvent
from .inventory_shelf_created_data import InventoryShelfCreatedData


class InventoryShelfCreatedEvent(InventoryEvent):
    """Represents the creation of an inventory shelf"""

    data_model: ClassVar[type[BaseModel] | None] = InventoryShelfCreatedData
