"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_item_updated."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_item_updated import ShoppingListItemUpdatedPayload


def test_fields_are_kept():
    payload = ShoppingListItemUpdatedPayload(list_id='sl1', item_id='i1')
    assert payload.list_id == 'sl1'
    assert payload.item_id == 'i1'


def test_schema_version_defaults_to_one():
    assert ShoppingListItemUpdatedPayload(list_id='sl1', item_id='i1').schema_version == 1


def test_list_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemUpdatedPayload(item_id='i1')


def test_item_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListItemUpdatedPayload(list_id='sl1')


def test_changed_defaults_to_empty():
    assert ShoppingListItemUpdatedPayload(list_id='sl1', item_id='i1').changed == []
