"""Tests for cynthus.messaging.common.signal.public_inventory_owner_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_owner_base import PublicInventoryOwnerSignalBase
from cynthus.messaging.common.signal.public_inventory_owner_requested import PublicInventoryOwnerRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryOwnerRequestedSignal.name == 'public.inventory.owner.requested'


def test_components():
    assert PublicInventoryOwnerRequestedSignal.visibility == 'public'
    assert PublicInventoryOwnerRequestedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryOwnerRequestedSignal.aggregate == 'owner'
    assert PublicInventoryOwnerRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryOwnerRequestedSignal, PublicInventoryOwnerSignalBase)
    assert issubclass(PublicInventoryOwnerRequestedSignal, SignalBase)
