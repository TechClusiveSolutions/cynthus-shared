"""Tests for cynthus.messaging.component.recipe.payload.recipe_responded."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.recipe.payload.recipe_responded import RecipeRespondedPayload


def test_required_fields_are_kept():
    payload = RecipeRespondedPayload(operation='get', status=200, result={'id': 'r1'})

    assert payload.operation == 'get'
    assert payload.status == 200
    assert payload.result == {'id': 'r1'}
    assert payload.error is None


def test_status_is_required():
    with pytest.raises(ValidationError):
        RecipeRespondedPayload(operation='get')
