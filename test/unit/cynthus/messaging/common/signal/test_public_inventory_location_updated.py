"""Tests for cynthus.messaging.common.signal.public_inventory_location_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_location_base import PublicInventoryLocationSignalBase
from cynthus.messaging.common.signal.public_inventory_location_updated import PublicInventoryLocationUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryLocationUpdatedSignal.name == 'public.inventory.location.updated'


def test_components():
    assert PublicInventoryLocationUpdatedSignal.visibility == 'public'
    assert PublicInventoryLocationUpdatedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryLocationUpdatedSignal.aggregate == 'location'
    assert PublicInventoryLocationUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryLocationUpdatedSignal, PublicInventoryLocationSignalBase)
    assert issubclass(PublicInventoryLocationUpdatedSignal, SignalBase)
