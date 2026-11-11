"""Tenant system model class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from .tenant_type import TenantType

from ..user import User

from ..redis import RedisClient


class Tenant(BaseModel):
    """Represents a tenant resource"""

    id_: UUID = Field(default_factory=uuid4)
    name: str
    type: TenantType
    owner: User
    # client: RedisClient = Field(default_factory=lambda: RedisClient.from_environment(), frozen=True)


    def get_workspaces(self) -> list[Workspace]:
        workspaces = list()
        key = 'A.B.C.D'

        # spaces = self.client.get(key)

        return workspaces
