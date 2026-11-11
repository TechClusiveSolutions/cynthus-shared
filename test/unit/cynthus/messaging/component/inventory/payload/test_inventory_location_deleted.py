"""Tests for cynthus.messaging.component.inventory.payload.inventory_location_deleted."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_location_deleted import InventoryLocationDeletedPayload


def test_required_fields_are_kept():
    payload = InventoryLocationDeletedPayload(location_id='x')

    assert payload.schema_version == 1
    assert payload.location_id == 'x'


def test_defaults():
    payload = InventoryLocationDeletedPayload(location_id='x')

    assert payload.metadata == {}


def test_location_id_is_required():
    with pytest.raises(ValidationError):
        InventoryLocationDeletedPayload()
