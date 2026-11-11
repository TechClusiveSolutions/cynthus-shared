"""Tests for cynthus.messaging.common.signal.public_inventory_item_responded."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_item_base import PublicInventoryItemSignalBase
from cynthus.messaging.common.signal.public_inventory_item_responded import PublicInventoryItemRespondedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryItemRespondedSignal.name == 'public.inventory.item.responded'


def test_components():
    assert PublicInventoryItemRespondedSignal.visibility == 'public'
    assert PublicInventoryItemRespondedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryItemRespondedSignal.aggregate == 'item'
    assert PublicInventoryItemRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryItemRespondedSignal, PublicInventoryItemSignalBase)
    assert issubclass(PublicInventoryItemRespondedSignal, SignalBase)
