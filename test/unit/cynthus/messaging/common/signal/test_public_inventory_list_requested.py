"""Tests for cynthus.messaging.common.signal.public_inventory_list_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_list_base import PublicInventoryListSignalBase
from cynthus.messaging.common.signal.public_inventory_list_requested import PublicInventoryListRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryListRequestedSignal.name == 'public.inventory.list.requested'


def test_components():
    assert PublicInventoryListRequestedSignal.visibility == 'public'
    assert PublicInventoryListRequestedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryListRequestedSignal.aggregate == 'list'
    assert PublicInventoryListRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryListRequestedSignal, PublicInventoryListSignalBase)
    assert issubclass(PublicInventoryListRequestedSignal, SignalBase)
