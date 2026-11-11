"""Tests for cynthus.messaging.common.signal.public_inventory_shelf_responded."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_shelf_base import PublicInventoryShelfSignalBase
from cynthus.messaging.common.signal.public_inventory_shelf_responded import PublicInventoryShelfRespondedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicInventoryShelfRespondedSignal.name == 'public.inventory.shelf.responded'


def test_components():
    assert PublicInventoryShelfRespondedSignal.visibility == 'public'
    assert PublicInventoryShelfRespondedSignal.domain is SignalDomainType.INVENTORY
    assert PublicInventoryShelfRespondedSignal.aggregate == 'shelf'
    assert PublicInventoryShelfRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicInventoryShelfRespondedSignal, PublicInventoryShelfSignalBase)
    assert issubclass(PublicInventoryShelfRespondedSignal, SignalBase)
