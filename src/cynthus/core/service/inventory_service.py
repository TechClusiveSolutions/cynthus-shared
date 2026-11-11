"""Inventory Service core model class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar
from uuid import UUID

from pydantic import Field

from ..event import EventRequest, InventoryEvent, InventoryEventRequest, UserEvent
from .service import Service
from .service_domain import ServiceDomain

SERVICE_ID = UUID('10000000-1000-1000-1000-100000000001')


class InventoryService(Service):
    """Represents the Inventory service application"""

    id_: UUID = Field(default=SERVICE_ID, frozen=True)
    name: str = Field(default='Inventory', frozen=True)
    domain: ServiceDomain = Field(default=ServiceDomain.CORE, frozen=True)

    event_class: ClassVar[type[UserEvent]] = InventoryEvent
    event_request_class: ClassVar[type[EventRequest]] = InventoryEventRequest
