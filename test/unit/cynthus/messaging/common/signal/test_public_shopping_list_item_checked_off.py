"""Tests for cynthus.messaging.common.signal.public_shopping_list_item_checked_off."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_item_base import PublicShoppingListItemSignalBase
from cynthus.messaging.common.signal.public_shopping_list_item_checked_off import PublicShoppingListItemCheckedOffSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListItemCheckedOffSignal.name == 'public.shopping_list.item.checked_off'


def test_components():
    assert PublicShoppingListItemCheckedOffSignal.visibility == 'public'
    assert PublicShoppingListItemCheckedOffSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListItemCheckedOffSignal.aggregate == 'item'
    assert PublicShoppingListItemCheckedOffSignal.action is SignalActionType.CHECKED_OFF


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListItemCheckedOffSignal, PublicShoppingListItemSignalBase)
    assert issubclass(PublicShoppingListItemCheckedOffSignal, SignalBase)
