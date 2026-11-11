"""Tests for cynthus.messaging.common.signal.public_recipe_recipe_deleted."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_recipe_recipe_base import PublicRecipeRecipeSignalBase
from cynthus.messaging.common.signal.public_recipe_recipe_deleted import PublicRecipeRecipeDeletedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicRecipeRecipeDeletedSignal.name == 'public.recipe.recipe.deleted'


def test_components():
    assert PublicRecipeRecipeDeletedSignal.visibility == 'public'
    assert PublicRecipeRecipeDeletedSignal.domain is SignalDomainType.RECIPE
    assert PublicRecipeRecipeDeletedSignal.aggregate == 'recipe'
    assert PublicRecipeRecipeDeletedSignal.action is SignalActionType.DELETED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicRecipeRecipeDeletedSignal, PublicRecipeRecipeSignalBase)
    assert issubclass(PublicRecipeRecipeDeletedSignal, SignalBase)
