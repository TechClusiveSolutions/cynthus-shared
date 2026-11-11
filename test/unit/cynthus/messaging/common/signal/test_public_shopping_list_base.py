"""Tests for cynthus.messaging.common.signal.public_shopping_list_base."""

from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_base import PublicShoppingListSignalBase


def test_public_shopping_list_signals_are_in_the_shopping_list_domain():
    assert PublicShoppingListSignalBase.visibility == 'public'
    assert PublicShoppingListSignalBase.domain is SignalDomainType.SHOPPING_LIST
    assert issubclass(PublicShoppingListSignalBase, SignalBase)
