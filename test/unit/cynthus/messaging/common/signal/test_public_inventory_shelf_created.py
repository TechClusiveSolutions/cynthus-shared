"""Tests for cynthus.messaging.common.signal.public_inventory_shelf_created."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_shelf_base import PublicInventoryShelfSignalBase
from cynthus.messaging.common.signal.public_inventory_shelf_created import PublicInventoryShelfCreatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryShelfCreatedSignal.name == 'public.inventory.shelf.created'


def test_components():
    assert PublicInventoryShelfCreatedSignal.visibility == 'public'
    assert PublicInventoryShelfCreatedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryShelfCreatedSignal.aggregate == 'shelf'
    assert PublicInventoryShelfCreatedSignal.action is SignalActionType.CREATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryShelfCreatedSignal, PublicInventoryShelfSignalBase)
    assert issubclass(PublicInventoryShelfCreatedSignal, SignalBase)
