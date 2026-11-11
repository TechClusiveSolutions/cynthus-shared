"""Tests for cynthus.messaging.component.inventory.payload.inventory_location_updated."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_location_updated import InventoryLocationUpdatedPayload


def test_required_fields_are_kept():
    payload = InventoryLocationUpdatedPayload(location_id='x')

    assert payload.schema_version == 1
    assert payload.location_id == 'x'


def test_defaults():
    payload = InventoryLocationUpdatedPayload(location_id='x')

    assert payload.name is None
    assert payload.type is None
    assert payload.archived is None


def test_location_id_is_required():
    with pytest.raises(ValidationError):
        InventoryLocationUpdatedPayload()
