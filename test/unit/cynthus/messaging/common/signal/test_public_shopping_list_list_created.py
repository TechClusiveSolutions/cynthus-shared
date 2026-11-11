"""Tests for cynthus.messaging.common.signal.public_shopping_list_list_created."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_shopping_list_list_base import PublicShoppingListListSignalBase
from cynthus.messaging.common.signal.public_shopping_list_list_created import PublicShoppingListListCreatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicShoppingListListCreatedSignal.name == 'public.shopping_list.list.created'


def test_components():
    assert PublicShoppingListListCreatedSignal.visibility == 'public'
    assert PublicShoppingListListCreatedSignal.domain is SignalDomainType.SHOPPING_LIST
    assert PublicShoppingListListCreatedSignal.aggregate == 'list'
    assert PublicShoppingListListCreatedSignal.action is SignalActionType.CREATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicShoppingListListCreatedSignal, PublicShoppingListListSignalBase)
    assert issubclass(PublicShoppingListListCreatedSignal, SignalBase)
