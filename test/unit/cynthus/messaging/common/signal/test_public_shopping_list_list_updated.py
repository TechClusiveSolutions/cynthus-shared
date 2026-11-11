"""Tests for cynthus.messaging.common.signal.public_shopping_list_list_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_list_base import PublicShoppingListListSignalBase
from cynthus.messaging.common.signal.public_shopping_list_list_updated import PublicShoppingListListUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListListUpdatedSignal.name == 'public.shopping_list.list.updated'


def test_components():
    assert PublicShoppingListListUpdatedSignal.visibility == 'public'
    assert PublicShoppingListListUpdatedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListListUpdatedSignal.aggregate == 'list'
    assert PublicShoppingListListUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListListUpdatedSignal, PublicShoppingListListSignalBase)
    assert issubclass(PublicShoppingListListUpdatedSignal, SignalBase)
