"""Tests for cynthus.messaging.component.recipe.payload.recipe_requested."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.recipe.payload.recipe_requested import RecipeRequestedPayload


def test_required_fields_are_kept():
    payload = RecipeRequestedPayload(operation='import_url', data={'url': 'https://example.com/r'})

    assert payload.schema_version == 1
    assert payload.operation == 'import_url'
    assert payload.data == {'url': 'https://example.com/r'}


def test_defaults():
    payload = RecipeRequestedPayload(operation='list')

    assert payload.resource_id is None
    assert payload.filters == {}
    assert payload.data == {}


def test_operation_is_required():
    with pytest.raises(ValidationError):
        RecipeRequestedPayload()


def test_unknown_operation_is_refused():
    with pytest.raises(ValidationError):
        RecipeRequestedPayload(operation='share')
