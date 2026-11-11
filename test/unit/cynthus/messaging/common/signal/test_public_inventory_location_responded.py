"""Tests for cynthus.messaging.common.signal.public_inventory_location_responded."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_location_base import PublicInventoryLocationSignalBase
from cynthus.messaging.common.signal.public_inventory_location_responded import PublicInventoryLocationRespondedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryLocationRespondedSignal.name == 'public.inventory.location.responded'


def test_components():
    assert PublicInventoryLocationRespondedSignal.visibility == 'public'
    assert PublicInventoryLocationRespondedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryLocationRespondedSignal.aggregate == 'location'
    assert PublicInventoryLocationRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryLocationRespondedSignal, PublicInventoryLocationSignalBase)
    assert issubclass(PublicInventoryLocationRespondedSignal, SignalBase)
