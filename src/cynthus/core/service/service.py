"""Service core model class for the Cynthus project"""

from __future__ import annotations

from typing import Any, ClassVar
from uuid import UUID

from pydantic import BaseModel

from ..event import EventAction, EventRequest, UserEvent
from ..resource import Resource
from ..system import System, Tenant, Workspace
from ..user import User
from .service_domain import ServiceDomain


class Service(BaseModel):
    """
        Represents a Cynthus service application

        This is the identity of a service (ADR-009): pure data, with no database, web framework or broker, so any code can
        use it and it can be serialized. The running parts of a service are joined to it by ``ServiceModule`` in
        ``cynthus.service``.
    """

    id_: UUID
    name: str
    domain: ServiceDomain

    # Subclasses name the kind of event and event request they build
    event_class: ClassVar[type[UserEvent]] = UserEvent
    event_request_class: ClassVar[type[EventRequest]] = EventRequest

    def build_event(
        self, *, tenant: Tenant, workspace: Workspace, resource: Resource, action: EventAction, user: User,
        data: dict[str, Any] | None = None,
    ) -> UserEvent:
        """An event for an action a user took on a resource, recorded by this service."""

        return self.event_class(
            tenant=tenant, workspace=workspace, resource=resource, action=action, user=user, data=data or {},
            service_id=self.id_,
        )

    def build_event_request(
        self, event: UserEvent, requestor: User | System, reason: str | None = None
    ) -> EventRequest:
        """A request for the action an event describes."""

        return self.event_request_class(event=event, requestor=requestor, reason=reason)
