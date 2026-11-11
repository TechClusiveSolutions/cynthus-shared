"""Tests for cynthus.messaging.component.inventory.payload.inventory_item_updated."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_item_updated import InventoryItemUpdatedPayload


def test_required_fields_are_kept():
    payload = InventoryItemUpdatedPayload(item_id='x', shelf_id='x', location_id='x')

    assert payload.schema_version == 1
    assert payload.item_id == 'x'
    assert payload.shelf_id == 'x'
    assert payload.location_id == 'x'


def test_defaults():
    payload = InventoryItemUpdatedPayload(item_id='x', shelf_id='x', location_id='x')

    assert payload.name is None
    assert payload.quantity is None
    assert payload.unit is None
    assert payload.low_threshold is None
    assert payload.expiry_date is None


def test_item_id_is_required():
    with pytest.raises(ValidationError):
        InventoryItemUpdatedPayload()
