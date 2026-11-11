"""Tests for cynthus.messaging.common.signal.public_shopping_list_list_deleted."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_list_base import PublicShoppingListListSignalBase
from cynthus.messaging.common.signal.public_shopping_list_list_deleted import PublicShoppingListListDeletedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListListDeletedSignal.name == 'public.shopping_list.list.deleted'


def test_components():
    assert PublicShoppingListListDeletedSignal.visibility == 'public'
    assert PublicShoppingListListDeletedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListListDeletedSignal.aggregate == 'list'
    assert PublicShoppingListListDeletedSignal.action is SignalActionType.DELETED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListListDeletedSignal, PublicShoppingListListSignalBase)
    assert issubclass(PublicShoppingListListDeletedSignal, SignalBase)
