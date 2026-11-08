"""Tests for cynthus.messaging.component.shopping_list.message.shopping_list_item_removed."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.shopping_list.message.shopping_list_item_removed import ShoppingListItemRemovedMessage
from cynthus.messaging.component.shopping_list.payload.shopping_list_item_removed import ShoppingListItemRemovedPayload


def make_message():
    return ShoppingListItemRemovedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ShoppingListItemRemovedPayload(list_id='sl1', item_id='i1'),
    )


def test_event_type():
    assert make_message().event_type == 'public.shopping_list.item.removed'


def test_round_trips_through_json():
    message = make_message()

    assert ShoppingListItemRemovedMessage.model_validate_json(message.model_dump_json()) == message
