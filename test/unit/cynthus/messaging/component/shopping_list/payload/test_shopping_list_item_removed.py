"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_item_removed."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_item_removed import ShoppingListItemRemovedPayload


def test_fields_are_kept():
    payload = ShoppingListItemRemovedPayload(list_id='sl1', item_id='i1')
    assert payload.list_id == 'sl1'
    assert payload.item_id == 'i1'


def test_schema_version_defaults_to_one():
    assert ShoppingListItemRemovedPayload(list_id='sl1', item_id='i1').schema_version == 1


def test_list_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemRemovedPayload(item_id='i1')


def test_item_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemRemovedPayload(list_id='sl1')
