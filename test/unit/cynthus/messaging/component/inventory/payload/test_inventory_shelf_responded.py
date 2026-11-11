"""Tests for cynthus.messaging.component.inventory.payload.inventory_shelf_responded."""

from cynthus.messaging.component.inventory.payload.inventory_responded_payload import InventoryRespondedPayload
from cynthus.messaging.component.inventory.payload.inventory_shelf_responded import InventoryShelfRespondedPayload


def test_it_is_the_shared_responded_payload():
    payload = InventoryShelfRespondedPayload(operation='list', status=200)

    assert isinstance(payload, InventoryRespondedPayload)
    assert payload.operation == 'list'
