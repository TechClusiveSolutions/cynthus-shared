"""Service identity unit tests for the Cynthus project"""

import pytest
from pydantic import ValidationError

from cynthus.core.event import Event, EventAction, EventRequest, InventoryEvent, InventoryEventRequest, UserEvent
from cynthus.core.resource import StorageLocation
from cynthus.core.service import (
    InventoryService,
    LogisticsService,
    ProfileService,
    RecipeService,
    Service,
    ServiceDomain,
    ShoppingService,
)
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User

SERVICES = [InventoryService, ProfileService, ShoppingService, LogisticsService, RecipeService]


@pytest.fixture
def scene():
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

    return user, tenant, workspace, location


def test_every_service_has_its_own_fixed_identity():
    services = [service() for service in SERVICES]

    assert len({service.id_ for service in services}) == len(SERVICES)
    assert len({service.name for service in services}) == len(SERVICES)
    assert all(service.domain == ServiceDomain.CORE for service in services)
    assert [service.name for service in services] == ['Inventory', 'Profile', 'Shopping', 'Logistics', 'Recipe']


def test_the_identity_is_the_same_each_time_it_is_built():
    assert InventoryService() == InventoryService()
    assert InventoryService().id_ == InventoryService().id_


@pytest.mark.parametrize('service_class', SERVICES)
def test_the_identity_cannot_be_changed(service_class):
    service = service_class()

    with pytest.raises(ValidationError):
        service.name = 'Other'

    with pytest.raises(ValidationError):
        service.id_ = service.id_


def test_a_service_serializes_to_its_identity_only():
    assert InventoryService().model_dump(mode='json') == {
        'id_': '10000000-1000-1000-1000-100000000001', 'name': 'Inventory', 'domain': 'core'}


def test_a_service_builds_an_event_that_names_it(scene):
    user, tenant, workspace, location = scene
    service = ProfileService()

    event = service.build_event(
        tenant=tenant, workspace=workspace, resource=location, action=EventAction.CREATED, user=user, data={'a': 1})

    assert type(event) is UserEvent
    assert event.service_id == service.id_
    assert event.user == user
    assert event.data == {'a': 1}


def test_an_event_without_data_has_an_empty_one(scene):
    user, tenant, workspace, location = scene

    event = ShoppingService().build_event(
        tenant=tenant, workspace=workspace, resource=location, action=EventAction.UPDATED, user=user)

    assert event.data == {}


def test_the_inventory_service_builds_inventory_events_and_requests(scene):
    user, tenant, workspace, location = scene
    service = InventoryService()

    event = service.build_event(
        tenant=tenant, workspace=workspace, resource=location, action=EventAction.ADDED, user=user)
    request = service.build_event_request(event, user, reason='stocking up')

    assert isinstance(event, InventoryEvent) and isinstance(event, Event)
    assert isinstance(request, InventoryEventRequest)
    assert request.event is event
    assert request.requestor == user
    assert request.reason == 'stocking up'


def test_another_service_builds_the_general_request(scene):
    user, tenant, workspace, location = scene
    service = RecipeService()
    event = service.build_event(
        tenant=tenant, workspace=workspace, resource=location, action=EventAction.RETRIEVED, user=user)

    request = service.build_event_request(event, user)

    assert type(request) is EventRequest
    assert request.reason is None


def test_the_base_service_needs_its_identity():
    with pytest.raises(ValidationError):
        Service()
