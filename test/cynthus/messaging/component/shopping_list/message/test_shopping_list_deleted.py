"""Tests for cynthus.messaging.component.shopping_list.message.shopping_list_deleted."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.shopping_list.message.shopping_list_deleted import ShoppingListDeletedMessage
from cynthus.messaging.component.shopping_list.payload.shopping_list_deleted import ShoppingListDeletedPayload


def make_message():
    return ShoppingListDeletedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ShoppingListDeletedPayload(list_id='sl1', owner_id='u1'),
    )


def test_event_type():
    assert make_message().event_type == 'public.shopping_list.list.deleted'


def test_round_trips_through_json():
    message = make_message()

    assert ShoppingListDeletedMessage.model_validate_json(message.model_dump_json()) == message
