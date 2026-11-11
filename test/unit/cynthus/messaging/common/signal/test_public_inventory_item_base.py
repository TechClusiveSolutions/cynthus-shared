"""Tests for cynthus.messaging.common.signal.public_inventory_item_base."""

from cynthus.messaging.common.signal.public_inventory_base import PublicInventorySignalBase
from cynthus.messaging.common.signal.public_inventory_item_base import PublicInventoryItemSignalBase


def test_item_base_sets_the_aggregate():
    assert PublicInventoryItemSignalBase.aggregate == 'item'
    assert issubclass(PublicInventoryItemSignalBase, PublicInventorySignalBase)
