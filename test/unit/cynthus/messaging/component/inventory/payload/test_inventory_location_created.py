"""Tests for cynthus.messaging.component.inventory.payload.inventory_location_created."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_location_created import InventoryLocationCreatedPayload


def test_required_fields_are_kept():
    payload = InventoryLocationCreatedPayload(location_id='x', name='x', type='x')

    assert payload.schema_version == 1
    assert payload.location_id == 'x'
    assert payload.name == 'x'
    assert payload.type == 'x'


def test_defaults():
    payload = InventoryLocationCreatedPayload(location_id='x', name='x', type='x')

    assert payload.metadata == {}


def test_location_id_is_required():
    with pytest.raises(ValidationError):
        InventoryLocationCreatedPayload()
