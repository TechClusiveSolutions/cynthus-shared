"""Tests for cynthus.messaging.common.signal.public_inventory_owner_added."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_owner_added import PublicInventoryOwnerAddedSignal
from cynthus.messaging.common.signal.public_inventory_owner_base import PublicInventoryOwnerSignalBase


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryOwnerAddedSignal.name == 'public.inventory.owner.added'


def test_components():
    assert PublicInventoryOwnerAddedSignal.visibility == 'public'
    assert PublicInventoryOwnerAddedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryOwnerAddedSignal.aggregate == 'owner'
    assert PublicInventoryOwnerAddedSignal.action is SignalActionType.ADDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryOwnerAddedSignal, PublicInventoryOwnerSignalBase)
    assert issubclass(PublicInventoryOwnerAddedSignal, SignalBase)
