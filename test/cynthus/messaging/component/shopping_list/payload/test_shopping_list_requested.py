"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_requested."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_requested import ShoppingListRequestedPayload


def test_required_fields_are_kept():
    payload = ShoppingListRequestedPayload(operation='add_item', resource_id='sl1', data={'name': 'Milk'})

    assert payload.schema_version == 1
    assert payload.operation == 'add_item'
    assert payload.resource_id == 'sl1'
    assert payload.data == {'name': 'Milk'}


def test_defaults():
    payload = ShoppingListRequestedPayload(operation='list')

    assert payload.resource_id is None
    assert payload.item_id is None
    assert payload.filters == {}
    assert payload.data == {}


def test_item_operations_carry_the_item():
    payload = ShoppingListRequestedPayload(operation='check_off_item', resource_id='sl1', item_id='i1')

    assert (payload.resource_id, payload.item_id) == ('sl1', 'i1')


def test_operation_is_required():
    with pytest.raises(ValidationError):
        ShoppingListRequestedPayload()


@pytest.mark.parametrize('operation', ['create', 'get', 'list', 'update', 'delete', 'add_item', 'update_item', 'remove_item', 'check_off_item'])
def test_every_documented_operation_is_accepted(operation):
    assert ShoppingListRequestedPayload(operation=operation).operation == operation


def test_unknown_operation_is_refused():
    with pytest.raises(ValidationError):
        ShoppingListRequestedPayload(operation='share')
