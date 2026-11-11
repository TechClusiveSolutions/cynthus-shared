"""Tests for cynthus.messaging.component.recipe.payload.recipe_deleted."""

from cynthus.messaging.component.recipe.payload.recipe_deleted import RecipeDeletedPayload


def test_fields_are_kept():
    payload = RecipeDeletedPayload(recipe_id='r1', owner_id='u1')

    assert (payload.recipe_id, payload.owner_id) == ('r1', 'u1')
