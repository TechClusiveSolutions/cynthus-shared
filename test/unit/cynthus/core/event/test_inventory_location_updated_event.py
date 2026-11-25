"""Tests for cynthus.core.event.inventory_location_updated_event (InventoryLocationUpdatedEvent)."""

import pytest
from pydantic import ValidationError

import cynthus.core.event as core_event
from cynthus.core.event import Event, EventAction, InventoryEvent, InventoryLocationUpdatedEvent, UserEvent
from cynthus.core.event.inventory_location_updated_data import InventoryLocationUpdatedData
from cynthus.core.event.inventory_location_updated_event import InventoryLocationUpdatedEvent as Direct
from cynthus.core.resource import StorageLocation
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User

_DATA = {'location_id': 'loc-1', 'archived': True}


def _make(data=None):
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

    return InventoryLocationUpdatedEvent(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, action=EventAction.UPDATED,
        data=dict(_DATA) if data is None else data, user=user,
    )


def test_is_exported_from_the_package():
    assert Direct is InventoryLocationUpdatedEvent
    assert core_event.InventoryLocationUpdatedEvent is InventoryLocationUpdatedEvent


def test_is_an_inventory_event():
    assert issubclass(InventoryLocationUpdatedEvent, InventoryEvent)
    assert issubclass(InventoryLocationUpdatedEvent, UserEvent)
    assert issubclass(InventoryLocationUpdatedEvent, Event)


def test_declares_its_data_model():
    assert InventoryLocationUpdatedEvent.data_model is InventoryLocationUpdatedData


def test_can_be_instantiated():
    event = _make()

    assert isinstance(event, InventoryLocationUpdatedEvent)
    assert event.data['location_id'] is not None


def test_event_type():
    assert _make().event_type == 'inventory_location_updated'


@pytest.mark.parametrize('missing', ['location_id'])
def test_missing_id_fails_at_creation(missing):
    data = {key: value for key, value in _DATA.items() if key != missing}

    with pytest.raises(ValidationError, match=missing):
        _make(data)


def test_empty_data_fails_at_creation():
    with pytest.raises(ValidationError):
        _make({})


def test_an_update_that_changes_nothing_fails_at_creation():
    with pytest.raises(ValidationError, match='must change'):
        _make({'location_id': 'loc-1'})

