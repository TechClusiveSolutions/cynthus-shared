"""Tests for cynthus.messaging.common.signal.public_inventory_shelf_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_shelf_base import PublicInventoryShelfSignalBase
from cynthus.messaging.common.signal.public_inventory_shelf_updated import PublicInventoryShelfUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryShelfUpdatedSignal.name == 'public.inventory.shelf.updated'


def test_components():
    assert PublicInventoryShelfUpdatedSignal.visibility == 'public'
    assert PublicInventoryShelfUpdatedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryShelfUpdatedSignal.aggregate == 'shelf'
    assert PublicInventoryShelfUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryShelfUpdatedSignal, PublicInventoryShelfSignalBase)
    assert issubclass(PublicInventoryShelfUpdatedSignal, SignalBase)
