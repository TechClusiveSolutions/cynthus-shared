"""Tests for cynthus.messaging.common.signal.public_inventory_location_deleted."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_location_base import PublicInventoryLocationSignalBase
from cynthus.messaging.common.signal.public_inventory_location_deleted import PublicInventoryLocationDeletedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryLocationDeletedSignal.name == 'public.inventory.location.deleted'


def test_components():
    assert PublicInventoryLocationDeletedSignal.visibility == 'public'
    assert PublicInventoryLocationDeletedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryLocationDeletedSignal.aggregate == 'location'
    assert PublicInventoryLocationDeletedSignal.action is SignalActionType.DELETED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryLocationDeletedSignal, PublicInventoryLocationSignalBase)
    assert issubclass(PublicInventoryLocationDeletedSignal, SignalBase)
