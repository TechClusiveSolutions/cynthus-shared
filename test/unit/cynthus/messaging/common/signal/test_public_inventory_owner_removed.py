"""Tests for cynthus.messaging.common.signal.public_inventory_owner_removed."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_owner_base import PublicInventoryOwnerSignalBase
from cynthus.messaging.common.signal.public_inventory_owner_removed import PublicInventoryOwnerRemovedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryOwnerRemovedSignal.name == 'public.inventory.owner.removed'


def test_components():
    assert PublicInventoryOwnerRemovedSignal.visibility == 'public'
    assert PublicInventoryOwnerRemovedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryOwnerRemovedSignal.aggregate == 'owner'
    assert PublicInventoryOwnerRemovedSignal.action is SignalActionType.REMOVED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryOwnerRemovedSignal, PublicInventoryOwnerSignalBase)
    assert issubclass(PublicInventoryOwnerRemovedSignal, SignalBase)
