"""Tests for cynthus.messaging.common.signal.public_recipe_recipe_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_recipe_recipe_base import PublicRecipeRecipeSignalBase
from cynthus.messaging.common.signal.public_recipe_recipe_requested import PublicRecipeRecipeRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicRecipeRecipeRequestedSignal.name == 'public.recipe.recipe.requested'


def test_components():
    assert PublicRecipeRecipeRequestedSignal.visibility == 'public'
    assert PublicRecipeRecipeRequestedSignal.domain is SignalDomainType.RECIPE
    assert PublicRecipeRecipeRequestedSignal.aggregate == 'recipe'
    assert PublicRecipeRecipeRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicRecipeRecipeRequestedSignal, PublicRecipeRecipeSignalBase)
    assert issubclass(PublicRecipeRecipeRequestedSignal, SignalBase)
