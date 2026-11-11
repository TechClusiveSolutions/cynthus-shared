"""Tests for cynthus.messaging.common.signal.public_inventory_list_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_list_base import PublicInventoryListSignalBase
from cynthus.messaging.common.signal.public_inventory_list_updated import PublicInventoryListUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryListUpdatedSignal.name == 'public.inventory.list.updated'


def test_components():
    assert PublicInventoryListUpdatedSignal.visibility == 'public'
    assert PublicInventoryListUpdatedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryListUpdatedSignal.aggregate == 'list'
    assert PublicInventoryListUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryListUpdatedSignal, PublicInventoryListSignalBase)
    assert issubclass(PublicInventoryListUpdatedSignal, SignalBase)
