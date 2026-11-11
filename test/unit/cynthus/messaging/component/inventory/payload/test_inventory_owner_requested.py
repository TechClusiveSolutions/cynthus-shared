"""Tests for cynthus.messaging.component.inventory.payload.inventory_owner_requested."""

from cynthus.messaging.component.inventory.payload.inventory_owner_requested import InventoryOwnerRequestedPayload
from cynthus.messaging.component.inventory.payload.inventory_requested_payload import InventoryRequestedPayload


def test_it_is_the_shared_requested_payload():
    payload = InventoryOwnerRequestedPayload(operation='list')

    assert isinstance(payload, InventoryRequestedPayload)
    assert payload.operation == 'list'
