"""Tests for cynthus.messaging.common.signal.public_shopping_list_list_responded."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_list_base import PublicShoppingListListSignalBase
from cynthus.messaging.common.signal.public_shopping_list_list_responded import PublicShoppingListListRespondedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListListRespondedSignal.name == 'public.shopping_list.list.responded'


def test_components():
    assert PublicShoppingListListRespondedSignal.visibility == 'public'
    assert PublicShoppingListListRespondedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListListRespondedSignal.aggregate == 'list'
    assert PublicShoppingListListRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListListRespondedSignal, PublicShoppingListListSignalBase)
    assert issubclass(PublicShoppingListListRespondedSignal, SignalBase)
