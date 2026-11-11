"""Inventory Service core model class for the Cynthus project"""

from __future__ import annotations

from pydantic import Field
from uuid import UUID

from .service import Service
from .service_domain import ServiceDomain

from ..event import InventoryEventRequest


SERVICE_ID = UUID('10000000-1000-1000-1000-100000000001')


class InventoryService(Service):
    """Represents the Inventory service application"""

    id_: UUID = Field(default=SERVICE_ID, frozen=True)
    name: str = Field(default='Inventory', frozen=True)
    domain: ServiceDomain = Field(default=ServiceDomain.CORE, frozen=True)

    def build_event(self) -> InventoryEvent:
        event = InventoryEvent()

        return event


    def build_event_request(self, ) -> InventoryEventRequest:
        event = self.build_event()
        request = InventoryEventRequest(event=event)

        return request

