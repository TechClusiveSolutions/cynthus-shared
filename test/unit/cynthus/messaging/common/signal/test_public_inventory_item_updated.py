"""Tests for cynthus.messaging.common.signal.public_inventory_item_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_item_base import PublicInventoryItemSignalBase
from cynthus.messaging.common.signal.public_inventory_item_updated import PublicInventoryItemUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryItemUpdatedSignal.name == 'public.inventory.item.updated'


def test_components():
    assert PublicInventoryItemUpdatedSignal.visibility == 'public'
    assert PublicInventoryItemUpdatedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryItemUpdatedSignal.aggregate == 'item'
    assert PublicInventoryItemUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryItemUpdatedSignal, PublicInventoryItemSignalBase)
    assert issubclass(PublicInventoryItemUpdatedSignal, SignalBase)
