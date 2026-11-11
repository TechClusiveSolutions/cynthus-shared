"""Tests for cynthus.messaging.common.signal.public_recipe_recipe_responded."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_recipe_recipe_base import PublicRecipeRecipeSignalBase
from cynthus.messaging.common.signal.public_recipe_recipe_responded import PublicRecipeRecipeRespondedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicRecipeRecipeRespondedSignal.name == 'public.recipe.recipe.responded'


def test_components():
    assert PublicRecipeRecipeRespondedSignal.visibility == 'public'
    assert PublicRecipeRecipeRespondedSignal.domain is SignalDomainType.RECIPE
    assert PublicRecipeRecipeRespondedSignal.aggregate == 'recipe'
    assert PublicRecipeRecipeRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicRecipeRecipeRespondedSignal, PublicRecipeRecipeSignalBase)
    assert issubclass(PublicRecipeRecipeRespondedSignal, SignalBase)
