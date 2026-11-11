"""Storage Location Shelf resource model class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from .storage_location import StorageLocation
from .storage_shelf import StorageShelf


class StorageLocationShelf(BaseModel):
    """Represents a storage shelf in a location resource"""

    id_: UUID = Field(default_factory=uuid4)
    location: StorageLocation
    shelf: StorageShelf
    position: str
