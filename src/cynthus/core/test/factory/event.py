"""Event factories for the Cynthus project"""

import factory

from ...event import (
    Event,
    EventAction,
    EventRequest,
    EventRequestDecision,
    EventRequestDecisionAnswer,
    EventRequestDecisionReason,
    EventRequestResponse,
    InventoryEvent,
    SystemEvent,
    UserEvent,
)
from .resource import StorageLocationFactory
from .system import TenantFactory, WorkspaceFactory


class EventFactory(factory.Factory):
    class Meta:
        model = Event

    tenant = factory.SubFactory(TenantFactory)
    workspace = factory.SubFactory(WorkspaceFactory, tenant=factory.SelfAttribute('..tenant'))
    resource = factory.SubFactory(StorageLocationFactory, workspace=factory.SelfAttribute('..workspace'))
    action = EventAction.CREATED
    data = factory.LazyFunction(dict)


class UserEventFactory(EventFactory):
    class Meta:
        model = UserEvent

    user = factory.SelfAttribute('tenant.owner')


class InventoryEventFactory(UserEventFactory):
    class Meta:
        model = InventoryEvent


class SystemEventFactory(EventFactory):
    class Meta:
        model = SystemEvent


class EventRequestFactory(factory.Factory):
    class Meta:
        model = EventRequest

    event = factory.SubFactory(UserEventFactory)
    requestor = factory.SelfAttribute('event.user')


class EventRequestDecisionFactory(factory.Factory):
    class Meta:
        model = EventRequestDecision

    answer = EventRequestDecisionAnswer.APPROVED
    reason = EventRequestDecisionReason.PERMITTED


class EventRequestResponseFactory(factory.Factory):
    class Meta:
        model = EventRequestResponse

    request = factory.SubFactory(EventRequestFactory)
