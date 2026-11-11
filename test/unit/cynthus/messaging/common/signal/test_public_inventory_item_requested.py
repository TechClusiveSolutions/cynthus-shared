"""Tests for cynthus.messaging.common.signal.public_inventory_item_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_item_base import PublicInventoryItemSignalBase
from cynthus.messaging.common.signal.public_inventory_item_requested import PublicInventoryItemRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryItemRequestedSignal.name == 'public.inventory.item.requested'


def test_components():
    assert PublicInventoryItemRequestedSignal.visibility == 'public'
    assert PublicInventoryItemRequestedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryItemRequestedSignal.aggregate == 'item'
    assert PublicInventoryItemRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryItemRequestedSignal, PublicInventoryItemSignalBase)
    assert issubclass(PublicInventoryItemRequestedSignal, SignalBase)
