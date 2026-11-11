"""Logistics Service core model class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from .service import Service
from .service_domain import ServiceDomain

SERVICE_ID = UUID('10000000-1000-1000-1000-100000000004')


class LogisticsService(Service):
    """Represents the Logistics service application"""

    id_: UUID = Field(default=SERVICE_ID, frozen=True)
    name: str = Field(default='Logistics', frozen=True)
    domain: ServiceDomain = Field(default=ServiceDomain.CORE, frozen=True)
