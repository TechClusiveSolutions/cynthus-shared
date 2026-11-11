"""Tests for cynthus.messaging.component.shopping_list.message.shopping_list_item_checked_off."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.shopping_list.message.shopping_list_item_checked_off import (
    ShoppingListItemCheckedOffMessage,
)
from cynthus.messaging.component.shopping_list.payload.shopping_list_item_checked_off import (
    ShoppingListItemCheckedOffPayload,
)


def make_message():
    return ShoppingListItemCheckedOffMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=ShoppingListItemCheckedOffPayload(list_id='sl1', item_id='i1', name='Whole milk'),
    )


def test_event_type():
    assert make_message().event_type == 'public.shopping_list.item.checked_off'


def test_round_trips_through_json():
    message = make_message()

    assert ShoppingListItemCheckedOffMessage.model_validate_json(message.model_dump_json()) == message
