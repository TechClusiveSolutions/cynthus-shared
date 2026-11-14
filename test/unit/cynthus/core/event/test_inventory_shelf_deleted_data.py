"""Tests for cynthus.core.event.inventory_shelf_deleted_data (InventoryShelfDeletedData)."""

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.inventory_shelf_deleted_data import InventoryShelfDeletedData


def test_is_a_pydantic_model():
    assert issubclass(InventoryShelfDeletedData, BaseModel)


def test_fields_are_exactly_the_contract():
    assert set(InventoryShelfDeletedData.model_fields) == {'shelf_id', 'location_id'}


def test_valid_data():
    data = InventoryShelfDeletedData(shelf_id='s-1', location_id='loc-1')

    assert data.shelf_id is not None
    assert data.location_id is not None


@pytest.mark.parametrize('missing', ['shelf_id', 'location_id'])
def test_required_ids(missing):
    values = dict(shelf_id='s-1', location_id='loc-1')
    del values[missing]

    with pytest.raises(ValidationError, match=missing):
        InventoryShelfDeletedData(**values)

