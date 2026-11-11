"""Resource model class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field

from ..soft_deletable import SoftDeletable


class Resource(SoftDeletable):
    """Represents a resource"""

    id_: UUID = Field(default_factory=uuid4)
    name: str
