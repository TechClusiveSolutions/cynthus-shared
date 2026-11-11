"""Tests for cynthus.messaging.common.signal.public_inventory_owner_responded."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_owner_base import PublicInventoryOwnerSignalBase
from cynthus.messaging.common.signal.public_inventory_owner_responded import PublicInventoryOwnerRespondedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryOwnerRespondedSignal.name == 'public.inventory.owner.responded'


def test_components():
    assert PublicInventoryOwnerRespondedSignal.visibility == 'public'
    assert PublicInventoryOwnerRespondedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryOwnerRespondedSignal.aggregate == 'owner'
    assert PublicInventoryOwnerRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryOwnerRespondedSignal, PublicInventoryOwnerSignalBase)
    assert issubclass(PublicInventoryOwnerRespondedSignal, SignalBase)
