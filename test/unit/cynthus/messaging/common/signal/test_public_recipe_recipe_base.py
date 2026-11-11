"""Tests for cynthus.messaging.common.signal.public_recipe_recipe_base."""

from cynthus.messaging.common.signal.public_recipe_base import PublicRecipeSignalBase
from cynthus.messaging.common.signal.public_recipe_recipe_base import PublicRecipeRecipeSignalBase


def test_recipe_base_sets_the_aggregate():
    assert PublicRecipeRecipeSignalBase.aggregate == 'recipe'
    assert issubclass(PublicRecipeRecipeSignalBase, PublicRecipeSignalBase)
