"""Tests for cynthus.messaging.component.inventory.message.inventory_shelf_responded."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_shelf_responded import InventoryShelfRespondedMessage
from cynthus.messaging.component.inventory.payload.inventory_shelf_responded import InventoryShelfRespondedPayload


def make_message():
    return InventoryShelfRespondedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryShelfRespondedPayload(operation='list', status=200),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.shelf.responded'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryShelfRespondedMessage.model_validate_json(message.model_dump_json()) == message
