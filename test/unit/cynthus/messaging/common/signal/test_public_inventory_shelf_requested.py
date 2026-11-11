"""Tests for cynthus.messaging.common.signal.public_inventory_shelf_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_shelf_base import PublicInventoryShelfSignalBase
from cynthus.messaging.common.signal.public_inventory_shelf_requested import PublicInventoryShelfRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryShelfRequestedSignal.name == 'public.inventory.shelf.requested'


def test_components():
    assert PublicInventoryShelfRequestedSignal.visibility == 'public'
    assert PublicInventoryShelfRequestedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryShelfRequestedSignal.aggregate == 'shelf'
    assert PublicInventoryShelfRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryShelfRequestedSignal, PublicInventoryShelfSignalBase)
    assert issubclass(PublicInventoryShelfRequestedSignal, SignalBase)
