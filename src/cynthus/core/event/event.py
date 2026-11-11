"""Event class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any
from uuid import UUID, uuid4

from .event_action import EventAction

from ..resource import Resource
from ..system import System, Tenant, Workspace
from ..user import User


class Event(BaseModel):
    """Represents an action taken on a resource"""

    id_: UUID = Field(default_factory=uuid4)
    tenant: Tenant
    workspace: Workspace
    correlation_id: UUID = Field(default_factory=uuid4)
    resource: Resource
    occurred_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: EventAction
    data: dict[str, Any]
