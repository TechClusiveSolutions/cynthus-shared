"""Tests for cynthus.core.event.inventory_location_created_data (InventoryLocationCreatedData)."""

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.inventory_location_created_data import InventoryLocationCreatedData


def test_is_a_pydantic_model():
    assert issubclass(InventoryLocationCreatedData, BaseModel)


def test_fields_are_exactly_the_contract():
    assert set(InventoryLocationCreatedData.model_fields) == {'location_id', 'name', 'type'}


def test_valid_data():
    data = InventoryLocationCreatedData(location_id='loc-1', name='Pantry', type='ambient')

    assert (data.location_id, data.name, data.type) == ('loc-1', 'Pantry', 'ambient')


@pytest.mark.parametrize('missing', ['location_id', 'name', 'type'])
def test_every_field_is_required(missing):
    values = {'location_id': 'loc-1', 'name': 'Pantry', 'type': 'ambient'}
    del values[missing]

    with pytest.raises(ValidationError, match=missing):
        InventoryLocationCreatedData(**values)


def test_wrongly_typed_field():
    with pytest.raises(ValidationError):
        InventoryLocationCreatedData(location_id={'a': 1}, name='Pantry', type='ambient')


def test_an_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        InventoryLocationCreatedData(location_id='l', name='n', type='ambient', misspelled=True)
