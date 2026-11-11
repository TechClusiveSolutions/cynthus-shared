"""Tenant system model class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from ..user import User
from .billing_account import BillingAccount
from .tenant_type import TenantType


class Tenant(BaseModel):
    """
        Represents a tenant: the boundary of data ownership, isolation and access

        When one owner has several tenants, a parent tenant ties them together (ADR-010). A parent is a ``bridge``: it has
        the same owner as its children and no workspaces, so no work is done in it.
    """

    id_: UUID = Field(default_factory=uuid4)
    name: str
    type: TenantType
    owner: User
    parent: Tenant | None = Field(default=None, description='The bridge tenant that groups this owner\'s tenants')
    bridge: bool = Field(default=False, description='True for a parent tenant, which has no workspaces')
    billing_account_id: UUID | None = None

    @model_validator(mode='after')
    def _check_parentage(self) -> Tenant:
        if self.parent is None:
            return self

        # Parents are one level deep (proposed in ADR-010, to be confirmed by the owner)
        if self.bridge:
            raise ValueError('a parent tenant cannot have a parent of its own')

        if not self.parent.bridge:
            raise ValueError('the parent of a tenant must be a bridge tenant')

        if self.parent.owner.id_ != self.owner.id_:
            raise ValueError('a tenant and its parent have the same owner')

        return self

    def attach_billing_account(self, account: BillingAccount) -> Tenant:
        """Bills this tenant to the account; the account must belong to the tenant's owner."""

        if account.owner.id_ != self.owner.id_:
            raise ValueError('a tenant can only be billed to an account of its owner')

        self.billing_account_id = account.id_

        return self
