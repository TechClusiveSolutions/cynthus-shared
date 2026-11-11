"""Tests for cynthus.messaging.common.signal.public_inventory_location_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_location_base import PublicInventoryLocationSignalBase
from cynthus.messaging.common.signal.public_inventory_location_requested import PublicInventoryLocationRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryLocationRequestedSignal.name == 'public.inventory.location.requested'


def test_components():
    assert PublicInventoryLocationRequestedSignal.visibility == 'public'
    assert PublicInventoryLocationRequestedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryLocationRequestedSignal.aggregate == 'location'
    assert PublicInventoryLocationRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryLocationRequestedSignal, PublicInventoryLocationSignalBase)
    assert issubclass(PublicInventoryLocationRequestedSignal, SignalBase)
