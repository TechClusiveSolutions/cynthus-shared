"""Tests for cynthus.messaging.common.signal.public_shopping_list_list_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_list_base import PublicShoppingListListSignalBase
from cynthus.messaging.common.signal.public_shopping_list_list_requested import PublicShoppingListListRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListListRequestedSignal.name == 'public.shopping_list.list.requested'


def test_components():
    assert PublicShoppingListListRequestedSignal.visibility == 'public'
    assert PublicShoppingListListRequestedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListListRequestedSignal.aggregate == 'list'
    assert PublicShoppingListListRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListListRequestedSignal, PublicShoppingListListSignalBase)
    assert issubclass(PublicShoppingListListRequestedSignal, SignalBase)
