"""Tests for cynthus.messaging.common.signal.public_recipe_recipe_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_recipe_recipe_base import PublicRecipeRecipeSignalBase
from cynthus.messaging.common.signal.public_recipe_recipe_updated import PublicRecipeRecipeUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicRecipeRecipeUpdatedSignal.name == 'public.recipe.recipe.updated'


def test_components():
    assert PublicRecipeRecipeUpdatedSignal.visibility == 'public'
    assert PublicRecipeRecipeUpdatedSignal.domain is SignalDomainType.RECIPE
    assert PublicRecipeRecipeUpdatedSignal.aggregate == 'recipe'
    assert PublicRecipeRecipeUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicRecipeRecipeUpdatedSignal, PublicRecipeRecipeSignalBase)
    assert issubclass(PublicRecipeRecipeUpdatedSignal, SignalBase)
