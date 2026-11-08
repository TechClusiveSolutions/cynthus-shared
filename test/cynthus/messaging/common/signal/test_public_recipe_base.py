"""Tests for cynthus.messaging.common.signal.public_recipe_base."""

from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_recipe_base import PublicRecipeSignalBase


def test_public_recipe_signals_are_in_the_recipe_domain():
    assert PublicRecipeSignalBase.visibility == 'public'
    assert PublicRecipeSignalBase.domain is SignalDomainType.RECIPE
    assert issubclass(PublicRecipeSignalBase, SignalBase)
