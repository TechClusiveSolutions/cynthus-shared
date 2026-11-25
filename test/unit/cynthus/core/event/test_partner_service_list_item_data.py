"""Tests for cynthus.core.event.partner_service_list_item_data (PartnerServiceListItemData)."""

from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.partner_service_list_item_data import PartnerServiceListItemData


def test_is_a_pydantic_model():
    assert issubclass(PartnerServiceListItemData, BaseModel)


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.PartnerServiceListItemData is PartnerServiceListItemData


def test_fields_are_exactly_the_contract():
    assert set(PartnerServiceListItemData.model_fields) == {'id', 'name'}


def test_valid_item():
    item_id = uuid4()
    item = PartnerServiceListItemData(id=item_id, name='Delivery')

    assert item.id == item_id
    assert item.name == 'Delivery'


def test_id_is_parsed_from_text():
    item_id = uuid4()

    assert PartnerServiceListItemData(id=str(item_id), name='x').id == item_id
    assert isinstance(PartnerServiceListItemData(id=str(item_id), name='x').id, UUID)


@pytest.mark.parametrize('missing', ['id', 'name'])
def test_required_fields(missing):
    values = {'id': uuid4(), 'name': 'x'}
    del values[missing]

    with pytest.raises(ValidationError):
        PartnerServiceListItemData(**values)


def test_id_must_be_a_uuid():
    with pytest.raises(ValidationError):
        PartnerServiceListItemData(id='not-a-uuid', name='x')


def test_name_must_be_a_string():
    with pytest.raises(ValidationError):
        PartnerServiceListItemData(id=uuid4(), name=5)


def test_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        PartnerServiceListItemData(id=uuid4(), name='x', other=1)


def test_extra_is_forbidden_in_the_config():
    assert PartnerServiceListItemData.model_config['extra'] == 'forbid'
