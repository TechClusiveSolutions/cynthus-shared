"""Tests for cynthus.messaging.component.recipe.payload.recipe_created."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.recipe.payload.recipe_created import RecipeCreatedPayload


def test_required_fields_are_kept():
    payload = RecipeCreatedPayload(recipe_id='r1', owner_id='u1', source='web', source_url='https://example.com/r')

    assert payload.source == 'web'
    assert payload.source_url == 'https://example.com/r'


def test_source_url_is_optional():
    assert RecipeCreatedPayload(recipe_id='r1', owner_id='u1', source='manual').source_url is None


def test_recipe_id_is_required():
    with pytest.raises(ValidationError):
        RecipeCreatedPayload(owner_id='u1', source='manual')
