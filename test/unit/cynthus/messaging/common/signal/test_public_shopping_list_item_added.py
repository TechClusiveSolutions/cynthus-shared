"""Tests for cynthus.messaging.common.signal.public_shopping_list_item_added."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_item_added import PublicShoppingListItemAddedSignal
from cynthus.messaging.common.signal.public_shopping_list_item_base import PublicShoppingListItemSignalBase


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListItemAddedSignal.name == 'public.shopping_list.item.added'


def test_components():
    assert PublicShoppingListItemAddedSignal.visibility == 'public'
    assert PublicShoppingListItemAddedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListItemAddedSignal.aggregate == 'item'
    assert PublicShoppingListItemAddedSignal.action is SignalActionType.ADDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListItemAddedSignal, PublicShoppingListItemSignalBase)
    assert issubclass(PublicShoppingListItemAddedSignal, SignalBase)
