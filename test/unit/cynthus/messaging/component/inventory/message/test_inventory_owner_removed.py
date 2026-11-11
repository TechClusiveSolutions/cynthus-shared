"""Tests for cynthus.messaging.component.inventory.message.inventory_owner_removed."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_owner_removed import InventoryOwnerRemovedMessage
from cynthus.messaging.component.inventory.payload.inventory_owner_removed import InventoryOwnerRemovedPayload


def make_message():
    return InventoryOwnerRemovedMessage(
        lifecycle_action=LifecycleAction.DELETED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryOwnerRemovedPayload(shelf_id='x', owner_id='y'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.owner.removed'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryOwnerRemovedMessage.model_validate_json(message.model_dump_json()) == message
