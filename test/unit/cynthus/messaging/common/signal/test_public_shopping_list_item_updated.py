"""Tests for cynthus.messaging.common.signal.public_shopping_list_item_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_item_base import PublicShoppingListItemSignalBase
from cynthus.messaging.common.signal.public_shopping_list_item_updated import PublicShoppingListItemUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListItemUpdatedSignal.name == 'public.shopping_list.item.updated'


def test_components():
    assert PublicShoppingListItemUpdatedSignal.visibility == 'public'
    assert PublicShoppingListItemUpdatedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListItemUpdatedSignal.aggregate == 'item'
    assert PublicShoppingListItemUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListItemUpdatedSignal, PublicShoppingListItemSignalBase)
    assert issubclass(PublicShoppingListItemUpdatedSignal, SignalBase)
