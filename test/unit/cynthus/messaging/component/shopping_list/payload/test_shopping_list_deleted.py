"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_deleted."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_deleted import ShoppingListDeletedPayload


def test_fields_are_kept():
    payload = ShoppingListDeletedPayload(list_id='sl1', owner_id='u1')
    assert payload.list_id == 'sl1'
    assert payload.owner_id == 'u1'


def test_schema_version_defaults_to_one():
    assert ShoppingListDeletedPayload(list_id='sl1', owner_id='u1').schema_version == 1


def test_list_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListDeletedPayload(owner_id='u1')


def test_owner_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListDeletedPayload(list_id='sl1')
