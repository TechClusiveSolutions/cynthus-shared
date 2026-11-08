"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_created."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_created import ShoppingListCreatedPayload


def test_fields_are_kept():
    payload = ShoppingListCreatedPayload(list_id='sl1', owner_id='u1', name='Weekly groceries', is_procurement_target=True)
    assert payload.list_id == 'sl1'
    assert payload.owner_id == 'u1'
    assert payload.name == 'Weekly groceries'
    assert payload.is_procurement_target is True


def test_schema_version_defaults_to_one():
    assert ShoppingListCreatedPayload(list_id='sl1', owner_id='u1', name='Weekly groceries').schema_version == 1


def test_list_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListCreatedPayload(owner_id='u1', name='Weekly groceries')


def test_owner_id_is_required():
    with pytest.raises(ValidationError):
        ShoppingListCreatedPayload(list_id='sl1', name='Weekly groceries')


def test_name_is_required():
    with pytest.raises(ValidationError):
        ShoppingListCreatedPayload(list_id='sl1', owner_id='u1')


def test_is_procurement_target_has_a_default():
    assert ShoppingListCreatedPayload(list_id='sl1', owner_id='u1', name='Weekly groceries').is_procurement_target is False
