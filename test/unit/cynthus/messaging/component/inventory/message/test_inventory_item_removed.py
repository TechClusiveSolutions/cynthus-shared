"""Tests for cynthus.messaging.component.inventory.message.inventory_item_removed."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_item_removed import InventoryItemRemovedMessage
from cynthus.messaging.component.inventory.payload.inventory_item_removed import InventoryItemRemovedPayload


def make_message():
    return InventoryItemRemovedMessage(
        lifecycle_action=LifecycleAction.DELETED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryItemRemovedPayload(item_id='x', shelf_id='x', location_id='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.item.removed'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryItemRemovedMessage.model_validate_json(message.model_dump_json()) == message
