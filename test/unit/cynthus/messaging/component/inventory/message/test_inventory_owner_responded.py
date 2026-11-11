"""Tests for cynthus.messaging.component.inventory.message.inventory_owner_responded."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_owner_responded import InventoryOwnerRespondedMessage
from cynthus.messaging.component.inventory.payload.inventory_owner_responded import InventoryOwnerRespondedPayload


def make_message():
    return InventoryOwnerRespondedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryOwnerRespondedPayload(operation='list', status=200),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.owner.responded'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryOwnerRespondedMessage.model_validate_json(message.model_dump_json()) == message
