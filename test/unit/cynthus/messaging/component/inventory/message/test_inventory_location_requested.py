"""Tests for cynthus.messaging.component.inventory.message.inventory_location_requested."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_location_requested import InventoryLocationRequestedMessage
from cynthus.messaging.component.inventory.payload.inventory_location_requested import InventoryLocationRequestedPayload


def make_message():
    return InventoryLocationRequestedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryLocationRequestedPayload(operation='list'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.location.requested'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryLocationRequestedMessage.model_validate_json(message.model_dump_json()) == message
