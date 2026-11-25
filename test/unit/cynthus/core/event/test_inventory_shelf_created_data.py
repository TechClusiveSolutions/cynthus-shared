"""Tests for cynthus.core.event.inventory_shelf_created_data (InventoryShelfCreatedData)."""

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.inventory_shelf_created_data import InventoryShelfCreatedData


def test_is_a_pydantic_model():
    assert issubclass(InventoryShelfCreatedData, BaseModel)


def test_fields_are_exactly_the_contract():
    assert set(InventoryShelfCreatedData.model_fields) == {'shelf_id', 'location_id', 'name', 'position'}


def test_valid_data():
    data = InventoryShelfCreatedData(shelf_id='s-1', location_id='loc-1', name='Top', position=3)

    assert (data.shelf_id, data.location_id, data.name, data.position) == ('s-1', 'loc-1', 'Top', 3)


def test_position_defaults_to_zero():
    assert InventoryShelfCreatedData(shelf_id='s-1', location_id='loc-1', name='Top').position == 0


@pytest.mark.parametrize('missing', ['shelf_id', 'location_id', 'name'])
def test_required_fields(missing):
    values = {'shelf_id': 's-1', 'location_id': 'loc-1', 'name': 'Top'}
    del values[missing]

    with pytest.raises(ValidationError, match=missing):
        InventoryShelfCreatedData(**values)


def test_position_must_be_an_integer():
    with pytest.raises(ValidationError, match='position'):
        InventoryShelfCreatedData(shelf_id='s-1', location_id='loc-1', name='Top', position='first')


def test_an_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        InventoryShelfCreatedData(shelf_id='s', location_id='l', name='n', misspelled=True)
