"""Tests for cynthus.messaging.common.signal.public_recipe_recipe_created."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_recipe_recipe_base import PublicRecipeRecipeSignalBase
from cynthus.messaging.common.signal.public_recipe_recipe_created import PublicRecipeRecipeCreatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicRecipeRecipeCreatedSignal.name == 'public.recipe.recipe.created'


def test_components():
    assert PublicRecipeRecipeCreatedSignal.visibility == 'public'
    assert PublicRecipeRecipeCreatedSignal.domain is SignalDomainType.RECIPE
    assert PublicRecipeRecipeCreatedSignal.aggregate == 'recipe'
    assert PublicRecipeRecipeCreatedSignal.action is SignalActionType.CREATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicRecipeRecipeCreatedSignal, PublicRecipeRecipeSignalBase)
    assert issubclass(PublicRecipeRecipeCreatedSignal, SignalBase)
