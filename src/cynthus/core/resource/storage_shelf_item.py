"""Storage Shelf Item resource model class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from .item import Item
from .storage_shelf import StorageShelf


class StorageShelfItem(BaseModel):
    """Represents a an item on a storage shelf resource"""

    id_: UUID = Field(default_factory=uuid4)
    shelf: StorageShelf
    item: Item
    x_position: int = Field(default=0)
    y_position: int = Field(default=0)
    z_position: int = Field(default=0)
