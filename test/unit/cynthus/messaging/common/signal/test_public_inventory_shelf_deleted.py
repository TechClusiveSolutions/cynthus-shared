"""Tests for cynthus.messaging.common.signal.public_inventory_shelf_deleted."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_shelf_base import PublicInventoryShelfSignalBase
from cynthus.messaging.common.signal.public_inventory_shelf_deleted import PublicInventoryShelfDeletedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryShelfDeletedSignal.name == 'public.inventory.shelf.deleted'


def test_components():
    assert PublicInventoryShelfDeletedSignal.visibility == 'public'
    assert PublicInventoryShelfDeletedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryShelfDeletedSignal.aggregate == 'shelf'
    assert PublicInventoryShelfDeletedSignal.action is SignalActionType.DELETED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryShelfDeletedSignal, PublicInventoryShelfSignalBase)
    assert issubclass(PublicInventoryShelfDeletedSignal, SignalBase)
