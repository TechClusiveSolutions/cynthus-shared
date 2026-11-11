"""Workspace system model class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from .tenant import Tenant

from ..user import User


class Workspace(BaseModel):
    """Represents a workspace resource"""

    id_: UUID = Field(default_factory=uuid4)
    name: str
    tenant: Tenant
    owner: User
