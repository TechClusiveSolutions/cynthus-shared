"""Tests for cynthus.messaging.component.shopping_list.message.shopping_list_item_added."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.shopping_list.message.shopping_list_item_added import ShoppingListItemAddedMessage
from cynthus.messaging.component.shopping_list.payload.shopping_list_item_added import ShoppingListItemAddedPayload


def make_message():
    return ShoppingListItemAddedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ShoppingListItemAddedPayload(list_id='sl1', item_id='i1', name='Whole milk'),
    )


def test_event_type():
    assert make_message().event_type == 'public.shopping_list.item.added'


def test_round_trips_through_json():
    message = make_message()

    assert ShoppingListItemAddedMessage.model_validate_json(message.model_dump_json()) == message
