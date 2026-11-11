"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_updated."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_updated import ShoppingListUpdatedPayload


def test_fields_are_kept():
    payload = ShoppingListUpdatedPayload(list_id='sl1', owner_id='u1')
    assert payload.list_id == 'sl1'
    assert payload.owner_id == 'u1'


def test_schema_version_defaults_to_one():
    assert ShoppingListUpdatedPayload(list_id='sl1', owner_id='u1').schema_version == 1


def test_list_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListUpdatedPayload(owner_id='u1')


def test_owner_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListUpdatedPayload(list_id='sl1')


def test_changed_defaults_to_empty():
    assert ShoppingListUpdatedPayload(list_id='sl1', owner_id='u1').changed == []
