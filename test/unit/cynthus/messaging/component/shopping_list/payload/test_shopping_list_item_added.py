"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_item_added."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_item_added import ShoppingListItemAddedPayload


def test_fields_are_kept():
    payload = ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk', quantity=2.0, unit='gal', notes='Organic if available', source='low_stock', catalog_item_id='cat1', inventory_item_id='inv1')
    assert payload.list_id == 'sl1'
    assert payload.item_id == 'i1'
    assert payload.name == 'Whole milk'
    assert payload.quantity == 2.0
    assert payload.unit == 'gal'
    assert payload.notes == 'Organic if available'
    assert payload.source == 'low_stock'
    assert payload.catalog_item_id == 'cat1'
    assert payload.inventory_item_id == 'inv1'


def test_schema_version_defaults_to_one():
    assert ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk').schema_version == 1


def test_list_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemAddedPayload(item_id='i1', name='Whole milk')


def test_item_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemAddedPayload(list_id='sl1', name='Whole milk')


def test_name_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemAddedPayload(list_id='sl1', item_id='i1')


def test_quantity_is_optional():
    assert ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk').quantity is None


@pytest.mark.parametrize('value', [0, -1.5])
def test_quantity_must_be_positive(value):
    with pytest.raises(ValidationError):
        ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk', quantity=value)


def test_unit_is_optional():
    assert ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk').unit is None


def test_notes_is_optional():
    assert ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk').notes is None


def test_catalog_item_id_is_optional():
    assert ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk').catalog_item_id is None


def test_inventory_item_id_is_optional():
    assert ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk').inventory_item_id is None


def test_source_has_a_default():
    assert ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk').source == 'manual'
