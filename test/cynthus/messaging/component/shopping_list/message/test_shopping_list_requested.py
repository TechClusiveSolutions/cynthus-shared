"""Tests for cynthus.messaging.component.shopping_list.message.shopping_list_requested."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.shopping_list.message.shopping_list_requested import ShoppingListRequestedMessage
from cynthus.messaging.component.shopping_list.payload.shopping_list_requested import ShoppingListRequestedPayload


def make_message():
    return ShoppingListRequestedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ShoppingListRequestedPayload(operation='list'),
    )


def test_event_type():
    assert make_message().event_type == 'public.shopping_list.list.requested'


def test_round_trips_through_json():
    message = make_message()

    assert ShoppingListRequestedMessage.model_validate_json(message.model_dump_json()) == message
