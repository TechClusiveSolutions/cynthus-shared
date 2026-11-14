'''Tests for cynthus.core.event.inventory_shelf_updated_data (InventoryShelfUpdatedData).'''

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.inventory_shelf_updated_data import InventoryShelfUpdatedData


def test_is_a_pydantic_model():
    assert issubclass(InventoryShelfUpdatedData, BaseModel)


def test_fields_are_exactly_the_contract():
    assert set(InventoryShelfUpdatedData.model_fields) == {'shelf_id', 'location_id', 'name', 'position'}


def test_name_alone_is_a_valid_change():
    data = InventoryShelfUpdatedData(shelf_id='s-1', location_id='loc-1', name='Top')

    assert data.name == 'Top'


def test_position_alone_is_a_valid_change():
    data = InventoryShelfUpdatedData(shelf_id='s-1', location_id='loc-1', position=2)

    assert data.position == 2


def test_unchanged_fields_are_none():
    data = InventoryShelfUpdatedData(shelf_id='s-1', location_id='loc-1', name='Top')

    assert data.position is None


def test_a_falsy_value_still_counts_as_a_change():
    data = InventoryShelfUpdatedData(shelf_id='s-1', location_id='loc-1', position=0)

    assert data.position == 0


def test_nothing_changed_is_refused():
    with pytest.raises(ValidationError, match='must change'):
        InventoryShelfUpdatedData(shelf_id='s-1', location_id='loc-1')


@pytest.mark.parametrize('missing', ['shelf_id', 'location_id'])
def test_required_ids(missing):
    values = dict(shelf_id='s-1', location_id='loc-1', name='Top')
    del values[missing]

    with pytest.raises(ValidationError, match=missing):
        InventoryShelfUpdatedData(**values)


def test_position_must_have_the_right_type():
    with pytest.raises(ValidationError, match='position'):
        InventoryShelfUpdatedData(shelf_id='s-1', location_id='loc-1', position='first')

