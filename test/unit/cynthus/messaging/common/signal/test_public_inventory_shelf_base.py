"""Tests for cynthus.messaging.common.signal.public_inventory_shelf_base."""

from cynthus.messaging.common.signal.public_inventory_base import PublicInventorySignalBase
from cynthus.messaging.common.signal.public_inventory_shelf_base import PublicInventoryShelfSignalBase


def test_shelf_base_sets_the_aggregate():
    assert PublicInventoryShelfSignalBase.aggregate == 'shelf'
    assert issubclass(PublicInventoryShelfSignalBase, PublicInventorySignalBase)
