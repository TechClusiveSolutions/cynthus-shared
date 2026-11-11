"""Tests for cynthus.messaging.component.inventory.message.inventory_location_created."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_location_created import InventoryLocationCreatedMessage
from cynthus.messaging.component.inventory.payload.inventory_location_created import InventoryLocationCreatedPayload


def make_message():
    return InventoryLocationCreatedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryLocationCreatedPayload(location_id='x', name='x', type='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.location.created'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryLocationCreatedMessage.model_validate_json(message.model_dump_json()) == message
