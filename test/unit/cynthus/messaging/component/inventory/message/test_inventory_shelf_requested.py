"""Tests for cynthus.messaging.component.inventory.message.inventory_shelf_requested."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_shelf_requested import InventoryShelfRequestedMessage
from cynthus.messaging.component.inventory.payload.inventory_shelf_requested import InventoryShelfRequestedPayload


def make_message():
    return InventoryShelfRequestedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryShelfRequestedPayload(operation='list'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.shelf.requested'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryShelfRequestedMessage.model_validate_json(message.model_dump_json()) == message
