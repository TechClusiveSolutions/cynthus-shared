"""Tests for cynthus.messaging.component.inventory.payload.inventory_shelf_deleted."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_shelf_deleted import InventoryShelfDeletedPayload


def test_required_fields_are_kept():
    payload = InventoryShelfDeletedPayload(shelf_id='x', location_id='x')

    assert payload.schema_version == 1
    assert payload.shelf_id == 'x'
    assert payload.location_id == 'x'


def test_defaults():
    payload = InventoryShelfDeletedPayload(shelf_id='x', location_id='x')

    assert payload.metadata == {}


def test_shelf_id_is_required():
    with pytest.raises(ValidationError):
        InventoryShelfDeletedPayload()
