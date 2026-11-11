"""Tests for cynthus.messaging.component.inventory.message.inventory_owner_added."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory.message.inventory_owner_added import InventoryOwnerAddedMessage
from cynthus.messaging.component.inventory.payload.inventory_owner_added import InventoryOwnerAddedPayload


def make_message():
    return InventoryOwnerAddedMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=InventoryOwnerAddedPayload(shelf_id='x', owner_id='y'),
    )


def test_event_type():
    assert make_message().event_type == 'public.inventory.owner.added'


def test_round_trips_through_json():
    message = make_message()

    assert InventoryOwnerAddedMessage.model_validate_json(message.model_dump_json()) == message
