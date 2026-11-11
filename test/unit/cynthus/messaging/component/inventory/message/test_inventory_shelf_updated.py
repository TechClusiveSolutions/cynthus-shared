"""Tests for cynthus.messaging.component.inventory.message.inventory_shelf_updated."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_shelf_updated import InventoryShelfUpdatedMessage
from cynthus.messaging.component.inventory.payload.inventory_shelf_updated import InventoryShelfUpdatedPayload


def make_message():
    return InventoryShelfUpdatedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryShelfUpdatedPayload(shelf_id='x', location_id='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.shelf.updated'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryShelfUpdatedMessage.model_validate_json(message.model_dump_json()) == message
