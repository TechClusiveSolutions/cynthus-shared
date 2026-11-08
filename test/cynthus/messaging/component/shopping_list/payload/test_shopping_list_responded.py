"""Tests for cynthus.messaging.component.shopping_list.payload.shopping_list_responded."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.shopping_list.payload.shopping_list_responded import ShoppingListRespondedPayload


def test_required_fields_are_kept():
    payload = ShoppingListRespondedPayload(operation='get', status=200, result={'id': 'sl1'})

    assert payload.operation == 'get'
    assert payload.status == 200
    assert payload.result == {'id': 'sl1'}
    assert payload.error is None


def test_an_error_answer_carries_the_reason():
    payload = ShoppingListRespondedPayload(operation='get', status=404, error='shopping list not found')

    assert (payload.result, payload.error) == (None, 'shopping list not found')


def test_status_is_required():
    with pytest.raises(ValidationError):
        ShoppingListRespondedPayload(operation='get')


def test_operation_is_required():
    with pytest.raises(ValidationError):
        ShoppingListRespondedPayload(status=200)
