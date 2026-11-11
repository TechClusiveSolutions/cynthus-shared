"""Tests for cynthus.messaging.component.inventory.message.inventory_item_added."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_item_added import InventoryItemAddedMessage
from cynthus.messaging.component.inventory.payload.inventory_item_added import InventoryItemAddedPayload


def make_message():
    return InventoryItemAddedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryItemAddedPayload(item_id='x', shelf_id='x', location_id='x', name='x', quantity=1.5),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.item.added'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryItemAddedMessage.model_validate_json(message.model_dump_json()) == message
