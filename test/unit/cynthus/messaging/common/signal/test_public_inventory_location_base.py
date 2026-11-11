"""Tests for cynthus.messaging.common.signal.public_inventory_location_base."""

from cynthus.messaging.common.signal.public_inventory_base import PublicInventorySignalBase
from cynthus.messaging.common.signal.public_inventory_location_base import PublicInventoryLocationSignalBase


def test_location_base_sets_the_aggregate():
    assert PublicInventoryLocationSignalBase.aggregate == 'location'
    assert issubclass(PublicInventoryLocationSignalBase, PublicInventorySignalBase)
