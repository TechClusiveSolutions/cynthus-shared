"""Tests for cynthus.messaging.common.signal.public_inventory_list_base and public_inventory_base."""

from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_inventory_base import PublicInventorySignalBase
from cynthus.messaging.common.signal.public_inventory_list_base import PublicInventoryListSignalBase


def test_inventory_base_sets_the_domain():
    assert PublicInventorySignalBase.domain is SignalDomainType.INVENTORY
    assert issubclass(PublicInventorySignalBase, SignalBase)


def test_list_base_sets_the_aggregate():
    assert PublicInventoryListSignalBase.aggregate == 'list'
    assert issubclass(PublicInventoryListSignalBase, PublicInventorySignalBase)
