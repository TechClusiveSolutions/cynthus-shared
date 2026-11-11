"""Tests for cynthus.messaging.common.signal.public_inventory_owner_base."""

from cynthus.messaging.common.signal.public_inventory_base import PublicInventorySignalBase
from cynthus.messaging.common.signal.public_inventory_owner_base import PublicInventoryOwnerSignalBase


def test_owner_base_sets_the_aggregate():
    assert PublicInventoryOwnerSignalBase.aggregate == 'owner'
    assert issubclass(PublicInventoryOwnerSignalBase, PublicInventorySignalBase)
