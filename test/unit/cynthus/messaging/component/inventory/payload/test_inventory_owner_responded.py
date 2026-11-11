"""Tests for cynthus.messaging.component.inventory.payload.inventory_owner_responded."""

from cynthus.messaging.component.inventory.payload.inventory_owner_responded import InventoryOwnerRespondedPayload
from cynthus.messaging.component.inventory.payload.inventory_responded_payload import InventoryRespondedPayload


def test_it_is_the_shared_responded_payload():
    payload = InventoryOwnerRespondedPayload(operation='list', status=200)

    assert isinstance(payload, InventoryRespondedPayload)
    assert payload.operation == 'list'
