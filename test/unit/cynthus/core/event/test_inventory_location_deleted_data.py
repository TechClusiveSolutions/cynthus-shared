"""Tests for cynthus.core.event.inventory_location_deleted_data (InventoryLocationDeletedData)."""

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.inventory_location_deleted_data import InventoryLocationDeletedData


def test_is_a_pydantic_model():
    assert issubclass(InventoryLocationDeletedData, BaseModel)


def test_fields_are_exactly_the_contract():
    assert set(InventoryLocationDeletedData.model_fields) == {'location_id'}


def test_valid_data():
    data = InventoryLocationDeletedData(location_id='loc-1')

    assert data.location_id is not None


@pytest.mark.parametrize('missing', ['location_id'])
def test_required_ids(missing):
    values = dict(location_id='loc-1')
    del values[missing]

    with pytest.raises(ValidationError, match=missing):
        InventoryLocationDeletedData(**values)

