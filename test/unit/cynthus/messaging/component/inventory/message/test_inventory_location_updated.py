"""Tests for cynthus.messaging.component.inventory.message.inventory_location_updated."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_location_updated import InventoryLocationUpdatedMessage
from cynthus.messaging.component.inventory.payload.inventory_location_updated import InventoryLocationUpdatedPayload


def make_message():
    return InventoryLocationUpdatedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryLocationUpdatedPayload(location_id='x'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.location.updated'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryLocationUpdatedMessage.model_validate_json(message.model_dump_json()) == message
