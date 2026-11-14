"""Tests for cynthus.core.event.inventory_location_created_event (InventoryLocationCreatedEvent)."""

import pytest
from pydantic import ValidationError

from cynthus.core.event import Event, EventAction, InventoryEvent, InventoryLocationCreatedEvent
from cynthus.core.event.inventory_location_created_data import InventoryLocationCreatedData
from cynthus.core.event.inventory_location_created_event import InventoryLocationCreatedEvent as Direct
from cynthus.core.resource import StorageLocation
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User

_DATA = {'location_id': 'loc-1', 'name': 'Pantry', 'type': 'ambient'}


def _make(data=None):
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

    return InventoryLocationCreatedEvent(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, action=EventAction.CREATED,
        data=dict(_DATA) if data is None else data, user=user,
    )


def test_is_exported_from_the_package():
    assert Direct is InventoryLocationCreatedEvent


def test_is_an_inventory_event():
    assert issubclass(InventoryLocationCreatedEvent, InventoryEvent)
    assert issubclass(InventoryLocationCreatedEvent, Event)


def test_adds_no_new_fields():
    assert set(InventoryLocationCreatedEvent.model_fields) == set(InventoryEvent.model_fields)


def test_declares_its_data_model():
    assert InventoryLocationCreatedEvent.data_model is InventoryLocationCreatedData


def test_can_be_instantiated():
    event = _make()

    assert isinstance(event, InventoryLocationCreatedEvent)
    assert event.correlation_id is not None


def test_event_type():
    assert _make().event_type == 'inventory_location_created'


@pytest.mark.parametrize('missing', ['location_id', 'name', 'type'])
def test_missing_data_field_fails_at_creation(missing):
    data = {key: value for key, value in _DATA.items() if key != missing}

    with pytest.raises(ValidationError, match=missing):
        _make(data)
