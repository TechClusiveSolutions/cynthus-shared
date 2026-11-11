"""Tests for cynthus.messaging.component.inventory.payload.inventory_item_added."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_item_added import InventoryItemAddedPayload


def test_required_fields_are_kept():
    payload = InventoryItemAddedPayload(item_id='x', shelf_id='x', location_id='x', name='x', quantity=1.5)

    assert payload.schema_version == 1
    assert payload.item_id == 'x'
    assert payload.shelf_id == 'x'
    assert payload.location_id == 'x'
    assert payload.name == 'x'
    assert payload.quantity == 1.5


def test_defaults():
    payload = InventoryItemAddedPayload(item_id='x', shelf_id='x', location_id='x', name='x', quantity=1.5)

    assert payload.unit is None
    assert payload.low_threshold is None
    assert payload.expiry_date is None
    assert payload.barcode is None
    assert payload.catalog_item_id is None


def test_item_id_is_required():
    with pytest.raises(ValidationError):
        InventoryItemAddedPayload()
