"""Tests for cynthus.messaging.component.inventory.message.inventory_shelf_created."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_shelf_created import InventoryShelfCreatedMessage
from cynthus.messaging.component.inventory.payload.inventory_shelf_created import InventoryShelfCreatedPayload


def make_message():
    return InventoryShelfCreatedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryShelfCreatedPayload(shelf_id='x', location_id='x', name='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.shelf.created'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryShelfCreatedMessage.model_validate_json(message.model_dump_json()) == message
