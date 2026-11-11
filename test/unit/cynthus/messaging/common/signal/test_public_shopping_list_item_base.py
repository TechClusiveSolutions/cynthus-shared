"""Tests for cynthus.messaging.common.signal.public_shopping_list_item_base."""

from cynthus.messaging.common.signal.public_shopping_list_base import PublicShoppingListSignalBase
from cynthus.messaging.common.signal.public_shopping_list_item_base import PublicShoppingListItemSignalBase


def test_item_base_sets_the_aggregate():
    assert PublicShoppingListItemSignalBase.aggregate == 'item'
    assert issubclass(PublicShoppingListItemSignalBase, PublicShoppingListSignalBase)
