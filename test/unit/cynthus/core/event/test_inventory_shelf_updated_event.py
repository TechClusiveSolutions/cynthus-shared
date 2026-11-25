"""Tests for cynthus.core.event.inventory_shelf_updated_event (InventoryShelfUpdatedEvent)."""

import pytest
from pydantic import ValidationError

import cynthus.core.event as core_event
from cynthus.core.event import Event, EventAction, InventoryEvent, InventoryShelfUpdatedEvent, UserEvent
from cynthus.core.event.inventory_shelf_updated_data import InventoryShelfUpdatedData
from cynthus.core.event.inventory_shelf_updated_event import InventoryShelfUpdatedEvent as Direct
from cynthus.core.resource import StorageLocation
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User

_DATA = {'shelf_id': 's-1', 'location_id': 'loc-1', 'name': 'Top shelf'}


def _make(data=None):
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

    return InventoryShelfUpdatedEvent(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, action=EventAction.UPDATED,
        data=dict(_DATA) if data is None else data, user=user,
    )


def test_is_exported_from_the_package():
    assert Direct is InventoryShelfUpdatedEvent
    assert core_event.InventoryShelfUpdatedEvent is InventoryShelfUpdatedEvent


def test_is_an_inventory_event():
    assert issubclass(InventoryShelfUpdatedEvent, InventoryEvent)
    assert issubclass(InventoryShelfUpdatedEvent, UserEvent)
    assert issubclass(InventoryShelfUpdatedEvent, Event)


def test_declares_its_data_model():
    assert InventoryShelfUpdatedEvent.data_model is InventoryShelfUpdatedData


def test_can_be_instantiated():
    event = _make()

    assert isinstance(event, InventoryShelfUpdatedEvent)
    assert event.data['shelf_id'] is not None


def test_event_type():
    assert _make().event_type == 'inventory_shelf_updated'


@pytest.mark.parametrize('missing', ['shelf_id', 'location_id'])
def test_missing_id_fails_at_creation(missing):
    data = {key: value for key, value in _DATA.items() if key != missing}

    with pytest.raises(ValidationError, match=missing):
        _make(data)


def test_empty_data_fails_at_creation():
    with pytest.raises(ValidationError):
        _make({})


def test_an_update_that_changes_nothing_fails_at_creation():
    with pytest.raises(ValidationError, match='must change'):
        _make({'shelf_id': 's-1', 'location_id': 'loc-1'})

