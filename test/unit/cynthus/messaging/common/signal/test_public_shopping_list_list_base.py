"""Tests for cynthus.messaging.common.signal.public_shopping_list_list_base."""

from cynthus.messaging.common.signal.public_shopping_list_base import PublicShoppingListSignalBase
from cynthus.messaging.common.signal.public_shopping_list_list_base import PublicShoppingListListSignalBase


def test_list_base_sets_the_aggregate():
    assert PublicShoppingListListSignalBase.aggregate == 'list'
    assert issubclass(PublicShoppingListListSignalBase, PublicShoppingListSignalBase)
