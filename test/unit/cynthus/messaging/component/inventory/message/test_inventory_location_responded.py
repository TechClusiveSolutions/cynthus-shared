"""Tests for cynthus.messaging.component.inventory.message.inventory_location_responded."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_location_responded import InventoryLocationRespondedMessage
from cynthus.messaging.component.inventory.payload.inventory_location_responded import InventoryLocationRespondedPayload


def make_message():
    return InventoryLocationRespondedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryLocationRespondedPayload(operation='list', status=200),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.location.responded'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryLocationRespondedMessage.model_validate_json(message.model_dump_json()) == message
