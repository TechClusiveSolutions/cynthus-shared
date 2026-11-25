'''Tests for cynthus.core.event.inventory_location_updated_data (InventoryLocationUpdatedData).'''

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.inventory_location_updated_data import InventoryLocationUpdatedData


def test_is_a_pydantic_model():
    assert issubclass(InventoryLocationUpdatedData, BaseModel)


def test_fields_are_exactly_the_contract():
    assert set(InventoryLocationUpdatedData.model_fields) == {'location_id', 'name', 'type', 'archived'}


def test_name_alone_is_a_valid_change():
    data = InventoryLocationUpdatedData(location_id='loc-1', name='Pantry')

    assert data.name == 'Pantry'


def test_type_alone_is_a_valid_change():
    data = InventoryLocationUpdatedData(location_id='loc-1', type='fridge')

    assert data.type == 'fridge'


def test_archived_alone_is_a_valid_change():
    data = InventoryLocationUpdatedData(location_id='loc-1', archived=True)

    assert data.archived is True


def test_unchanged_fields_are_none():
    data = InventoryLocationUpdatedData(location_id='loc-1', name='Pantry')

    assert data.type is None
    assert data.archived is None


def test_a_falsy_value_still_counts_as_a_change():
    data = InventoryLocationUpdatedData(location_id='loc-1', archived=False)

    assert data.archived is False


def test_nothing_changed_is_refused():
    with pytest.raises(ValidationError, match='must change'):
        InventoryLocationUpdatedData(location_id='loc-1')


@pytest.mark.parametrize('missing', ['location_id'])
def test_required_ids(missing):
    values = dict(location_id='loc-1', name='Pantry')
    del values[missing]

    with pytest.raises(ValidationError, match=missing):
        InventoryLocationUpdatedData(**values)


def test_archived_must_have_the_right_type():
    with pytest.raises(ValidationError, match='archived'):
        InventoryLocationUpdatedData(location_id='loc-1', archived='maybe')


def test_an_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        InventoryLocationUpdatedData(location_id='l', name='n', misspelled=True)
