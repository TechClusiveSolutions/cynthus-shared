"""Tests for cynthus.messaging.component.inventory.payload.inventory_item_responded."""

from cynthus.messaging.component.inventory.payload.inventory_item_responded import InventoryItemRespondedPayload
from cynthus.messaging.component.inventory.payload.inventory_responded_payload import InventoryRespondedPayload


def test_it_is_the_shared_responded_payload():
    payload = InventoryItemRespondedPayload(operation='list', status=200)

    assert isinstance(payload, InventoryRespondedPayload)
    assert payload.operation == 'list'
