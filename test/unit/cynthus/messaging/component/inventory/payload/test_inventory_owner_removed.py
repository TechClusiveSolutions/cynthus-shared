"""Tests for cynthus.messaging.component.inventory.payload.inventory_owner_removed."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_owner_removed import InventoryOwnerRemovedPayload


def test_required_fields_are_kept():
    payload = InventoryOwnerRemovedPayload(shelf_id='x', owner_id='y')

    assert payload.schema_version == 1
    assert payload.shelf_id == 'x'
    assert payload.owner_id == 'y'


def test_shelf_id_is_required():
    with pytest.raises(ValidationError):
        InventoryOwnerRemovedPayload(owner_id='y')


def test_owner_id_is_required():
    with pytest.raises(ValidationError):
        InventoryOwnerRemovedPayload(shelf_id='x')
