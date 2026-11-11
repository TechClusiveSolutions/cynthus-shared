"""Event fixtures for the Cynthus project"""

from pytest import fixture

from ...event import (
    Event,
    EventRequest,
    EventRequestDecision,
    EventRequestResponse,
    InventoryEvent,
    SystemEvent,
    UserEvent,
)
from ..factory import (
    EventFactory,
    EventRequestDecisionFactory,
    EventRequestFactory,
    EventRequestResponseFactory,
    InventoryEventFactory,
    SystemEventFactory,
    UserEventFactory,
)


@fixture
def event() -> Event:
    return EventFactory()


@fixture
def user_event() -> UserEvent:
    return UserEventFactory()


@fixture
def inventory_event() -> InventoryEvent:
    return InventoryEventFactory()


@fixture
def system_event() -> SystemEvent:
    return SystemEventFactory()


@fixture
def event_request() -> EventRequest:
    return EventRequestFactory()


@fixture
def event_request_decision() -> EventRequestDecision:
    return EventRequestDecisionFactory()


@fixture
def event_request_response() -> EventRequestResponse:
    return EventRequestResponseFactory()
