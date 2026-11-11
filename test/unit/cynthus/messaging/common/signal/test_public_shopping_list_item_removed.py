"""Tests for cynthus.messaging.common.signal.public_shopping_list_item_removed."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_item_base import PublicShoppingListItemSignalBase
from cynthus.messaging.common.signal.public_shopping_list_item_removed import PublicShoppingListItemRemovedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListItemRemovedSignal.name == 'public.shopping_list.item.removed'


def test_components():
    assert PublicShoppingListItemRemovedSignal.visibility == 'public'
    assert PublicShoppingListItemRemovedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListItemRemovedSignal.aggregate == 'item'
    assert PublicShoppingListItemRemovedSignal.action is SignalActionType.REMOVED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListItemRemovedSignal, PublicShoppingListItemSignalBase)
    assert issubclass(PublicShoppingListItemRemovedSignal, SignalBase)
