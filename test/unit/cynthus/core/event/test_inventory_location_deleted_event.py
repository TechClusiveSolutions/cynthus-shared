"""Tests for cynthus.core.event.inventory_location_deleted_event (InventoryLocationDeletedEvent)."""

import pytest
from pydantic import ValidationError

import cynthus.core.event as core_event
from cynthus.core.event import Event, EventAction, InventoryEvent, InventoryLocationDeletedEvent, UserEvent
from cynthus.core.event.inventory_location_deleted_data import InventoryLocationDeletedData
from cynthus.core.event.inventory_location_deleted_event import InventoryLocationDeletedEvent as Direct
from cynthus.core.resource import StorageLocation
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User

_DATA = {'location_id': 'loc-1'}


def _make(data=None):
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

    return InventoryLocationDeletedEvent(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, action=EventAction.DELETED,
        data=dict(_DATA) if data is None else data, user=user,
    )


def test_is_exported_from_the_package():
    assert Direct is InventoryLocationDeletedEvent
    assert core_event.InventoryLocationDeletedEvent is InventoryLocationDeletedEvent


def test_is_an_inventory_event():
    assert issubclass(InventoryLocationDeletedEvent, InventoryEvent)
    assert issubclass(InventoryLocationDeletedEvent, UserEvent)
    assert issubclass(InventoryLocationDeletedEvent, Event)


def test_declares_its_data_model():
    assert InventoryLocationDeletedEvent.data_model is InventoryLocationDeletedData


def test_can_be_instantiated():
    event = _make()

    assert isinstance(event, InventoryLocationDeletedEvent)
    assert event.data['location_id'] is not None


def test_event_type():
    assert _make().event_type == 'inventory_location_deleted'


@pytest.mark.parametrize('missing', ['location_id'])
def test_missing_id_fails_at_creation(missing):
    data = {key: value for key, value in _DATA.items() if key != missing}

    with pytest.raises(ValidationError, match=missing):
        _make(data)


def test_empty_data_fails_at_creation():
    with pytest.raises(ValidationError):
        _make({})

