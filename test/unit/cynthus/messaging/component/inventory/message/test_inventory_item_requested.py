"""Tests for cynthus.messaging.component.inventory.message.inventory_item_requested."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_item_requested import InventoryItemRequestedMessage
from cynthus.messaging.component.inventory.payload.inventory_item_requested import InventoryItemRequestedPayload


def make_message():
    return InventoryItemRequestedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryItemRequestedPayload(operation='list'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.item.requested'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryItemRequestedMessage.model_validate_json(message.model_dump_json()) == message
