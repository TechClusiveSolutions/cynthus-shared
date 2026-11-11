"""Billing Account system model class for the Cynthus project"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from ..soft_deletable import SoftDeletable
from ..user import User


class BillingAccount(SoftDeletable):
    """
        Represents a billing account

        An owner has one or more billing accounts and chooses which one is attached to each tenant, the same or a
        different one (ADR-010). Each account sets its own options.
    """

    id_: UUID = Field(default_factory=uuid4)
    owner: User
    name: str
    options: dict[str, Any] = Field(default_factory=dict)
