"""Tests for cynthus.messaging.component.inventory.message.inventory_location_deleted."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_location_deleted import InventoryLocationDeletedMessage
from cynthus.messaging.component.inventory.payload.inventory_location_deleted import InventoryLocationDeletedPayload


def make_message():
    return InventoryLocationDeletedMessage(
        lifecycle_action=LifecycleAction.DELETED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryLocationDeletedPayload(location_id='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.location.deleted'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryLocationDeletedMessage.model_validate_json(message.model_dump_json()) == message
