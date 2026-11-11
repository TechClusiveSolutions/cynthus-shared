"""Tests for cynthus.messaging.component.inventory.payload.inventory_owner_added."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_owner_added import InventoryOwnerAddedPayload


def test_required_fields_are_kept():
    payload = InventoryOwnerAddedPayload(shelf_id='x', owner_id='y')

    assert payload.schema_version == 1
    assert payload.shelf_id == 'x'
    assert payload.owner_id == 'y'
    assert payload.granted_by is None


def test_shelf_id_is_required():
    with pytest.raises(ValidationError):
        InventoryOwnerAddedPayload(owner_id='y')


def test_owner_id_is_required():
    with pytest.raises(ValidationError):
        InventoryOwnerAddedPayload(shelf_id='x')
