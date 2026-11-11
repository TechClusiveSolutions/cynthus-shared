"""Workspace system model class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field, model_validator

from ..soft_deletable import SoftDeletable
from ..user import User
from .tenant import Tenant


class Workspace(SoftDeletable):
    """Represents a workspace resource"""

    id_: UUID = Field(default_factory=uuid4)
    name: str
    tenant: Tenant
    owner: User

    @model_validator(mode='after')
    def _check_tenant(self) -> Workspace:
        if self.tenant.bridge:
            raise ValueError('a parent tenant has no workspaces')

        return self
