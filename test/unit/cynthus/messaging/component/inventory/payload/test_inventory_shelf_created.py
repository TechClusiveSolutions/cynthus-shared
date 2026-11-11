"""Tests for cynthus.messaging.component.inventory.payload.inventory_shelf_created."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_shelf_created import InventoryShelfCreatedPayload


def test_required_fields_are_kept():
    payload = InventoryShelfCreatedPayload(shelf_id='x', location_id='x', name='x')

    assert payload.schema_version == 1
    assert payload.shelf_id == 'x'
    assert payload.location_id == 'x'
    assert payload.name == 'x'


def test_defaults():
    payload = InventoryShelfCreatedPayload(shelf_id='x', location_id='x', name='x')

    assert payload.position == 0


def test_shelf_id_is_required():
    with pytest.raises(ValidationError):
        InventoryShelfCreatedPayload()
