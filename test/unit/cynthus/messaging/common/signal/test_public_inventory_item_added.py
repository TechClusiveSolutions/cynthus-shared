"""Tests for cynthus.messaging.common.signal.public_inventory_item_added."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_item_added import PublicInventoryItemAddedSignal
from cynthus.messaging.common.signal.public_inventory_item_base import PublicInventoryItemSignalBase


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryItemAddedSignal.name == 'public.inventory.item.added'


def test_components():
    assert PublicInventoryItemAddedSignal.visibility == 'public'
    assert PublicInventoryItemAddedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryItemAddedSignal.aggregate == 'item'
    assert PublicInventoryItemAddedSignal.action is SignalActionType.ADDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryItemAddedSignal, PublicInventoryItemSignalBase)
    assert issubclass(PublicInventoryItemAddedSignal, SignalBase)
