"""Resource model class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Resource(BaseModel):
    """Represents a resource"""

    id_: UUID = Field(default_factory=uuid4)
    name: str
