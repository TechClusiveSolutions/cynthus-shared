"""Tests for cynthus.messaging.component.inventory.payload.inventory_shelf_requested."""

from cynthus.messaging.component.inventory.payload.inventory_requested_payload import InventoryRequestedPayload
from cynthus.messaging.component.inventory.payload.inventory_shelf_requested import InventoryShelfRequestedPayload


def test_it_is_the_shared_requested_payload():
    payload = InventoryShelfRequestedPayload(operation='list')

    assert isinstance(payload, InventoryRequestedPayload)
    assert payload.operation == 'list'
