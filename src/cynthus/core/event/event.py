"""Event class for the Cynthus project"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from ..resource import Resource
from ..system import Tenant, Workspace
from .event_action import EventAction


class Event(BaseModel):
    """Represents an action taken on a resource"""

    id_: UUID = Field(default_factory=uuid4)
    tenant: Tenant
    workspace: Workspace
    correlation_id: UUID = Field(default_factory=uuid4)
    service_id: UUID | None = Field(default=None, description='The service that recorded the event')
    resource: Resource
    occurred_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: EventAction
    data: dict[str, Any]

    data_model: ClassVar[type[BaseModel] | None] = None

    @model_validator(mode='after')
    def _validate_data(self) -> Event:
        """Check ``data`` against ``data_model`` when the event class declares one"""

        if self.data_model is not None:
            self.data_model.model_validate(self.data)

        return self

    @property
    def event_type(self) -> str:
        """The snake_case class name without a trailing ``Event`` (``InventoryLocationCreatedEvent`` is
        ``inventory_location_created``; a class named exactly ``Event`` is ``event``)"""

        name = type(self).__name__
        name = name.removesuffix('Event') or name
        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)

        return name.lower()
