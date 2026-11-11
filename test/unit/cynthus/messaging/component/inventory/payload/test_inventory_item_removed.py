"""Tests for cynthus.messaging.component.inventory.payload.inventory_item_removed."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_item_removed import InventoryItemRemovedPayload


def test_required_fields_are_kept():
    payload = InventoryItemRemovedPayload(item_id='x', shelf_id='x', location_id='x')

    assert payload.schema_version == 1
    assert payload.item_id == 'x'
    assert payload.shelf_id == 'x'
    assert payload.location_id == 'x'


def test_defaults():
    payload = InventoryItemRemovedPayload(item_id='x', shelf_id='x', location_id='x')

    assert payload.metadata == {}


def test_item_id_is_required():
    with pytest.raises(ValidationError):
        InventoryItemRemovedPayload()
