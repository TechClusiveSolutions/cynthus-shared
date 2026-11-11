"""Tests for cynthus.messaging.common.signal.public_inventory_item_removed."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_item_base import PublicInventoryItemSignalBase
from cynthus.messaging.common.signal.public_inventory_item_removed import PublicInventoryItemRemovedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryItemRemovedSignal.name == 'public.inventory.item.removed'


def test_components():
    assert PublicInventoryItemRemovedSignal.visibility == 'public'
    assert PublicInventoryItemRemovedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryItemRemovedSignal.aggregate == 'item'
    assert PublicInventoryItemRemovedSignal.action is SignalActionType.REMOVED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryItemRemovedSignal, PublicInventoryItemSignalBase)
    assert issubclass(PublicInventoryItemRemovedSignal, SignalBase)
