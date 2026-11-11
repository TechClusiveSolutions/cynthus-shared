"""Tests for cynthus.messaging.component.recipe.payload.recipe_updated."""

from cynthus.messaging.component.recipe.payload.recipe_updated import RecipeUpdatedPayload


def test_changed_defaults_to_empty():
    assert RecipeUpdatedPayload(recipe_id='r1', owner_id='u1').changed == []


def test_changed_is_kept():
    assert RecipeUpdatedPayload(recipe_id='r1', owner_id='u1', changed=['title']).changed == ['title']
