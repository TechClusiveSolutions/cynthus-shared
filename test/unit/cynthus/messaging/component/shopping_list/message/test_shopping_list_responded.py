"""Tests for cynthus.messaging.component.shopping_list.message.shopping_list_responded."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.shopping_list.message.shopping_list_responded import ShoppingListRespondedMessage
from cynthus.messaging.component.shopping_list.payload.shopping_list_responded import ShoppingListRespondedPayload


def make_message():
    return ShoppingListRespondedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ShoppingListRespondedPayload(operation='list', status=200),
    )


def test_event_type():
    assert make_message().event_type == 'public.shopping_list.list.responded'


def test_round_trips_through_json():
    message = make_message()

    assert ShoppingListRespondedMessage.model_validate_json(message.model_dump_json()) == message
