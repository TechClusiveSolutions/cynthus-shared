"""Tests for cynthus.messaging.common.signal.public_inventory_location_created."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_location_base import PublicInventoryLocationSignalBase
from cynthus.messaging.common.signal.public_inventory_location_created import PublicInventoryLocationCreatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryLocationCreatedSignal.name == 'public.inventory.location.created'


def test_components():
    assert PublicInventoryLocationCreatedSignal.visibility == 'public'
    assert PublicInventoryLocationCreatedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryLocationCreatedSignal.aggregate == 'location'
    assert PublicInventoryLocationCreatedSignal.action is SignalActionType.CREATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryLocationCreatedSignal, PublicInventoryLocationSignalBase)
    assert issubclass(PublicInventoryLocationCreatedSignal, SignalBase)
