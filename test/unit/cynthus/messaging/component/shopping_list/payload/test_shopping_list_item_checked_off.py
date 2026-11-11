"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_item_checked_off."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_item_checked_off import (
    ShoppingListItemCheckedOffPayload,
)


def test_fields_are_kept():
    payload = ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1', name='Whole milk', quantity_purchased=2.0, unit='gal', provider_id='p1')
    assert payload.list_id == 'sl1'
    assert payload.item_id == 'i1'
    assert payload.name == 'Whole milk'
    assert payload.quantity_purchased == 2.0
    assert payload.unit == 'gal'
    assert payload.provider_id == 'p1'


def test_schema_version_defaults_to_one():
    assert ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1', name='Whole milk').schema_version == 1


def test_list_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemCheckedOffPayload(item_id='i1', name='Whole milk')


def test_item_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemCheckedOffPayload(list_id='sl1', name='Whole milk')


def test_name_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1')


def test_quantity_purchased_is_optional():
    assert ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1', name='Whole milk').quantity_purchased is None


@pytest.mark.parametrize('value', [0, -1.5])
def test_quantity_purchased_must_be_positive(value):
    with pytest.raises(ValidationError):
        ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1', name='Whole milk', quantity_purchased=value)


def test_unit_is_optional():
    assert ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1', name='Whole milk').unit is None


def test_provider_id_is_optional():
    assert ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1', name='Whole milk').provider_id is None
