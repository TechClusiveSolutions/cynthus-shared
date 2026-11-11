"""Tests for the inventory list message classes."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.inventory import (
    InventoryListRequestedMessage,
    InventoryListRequestedPayload,
    InventoryListUpdatedMessage,
    InventoryListUpdatedPayload,
)


def envelope(**extra):
    return dict(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        **extra,
    )


def test_requested_message_event_type():
    message = InventoryListRequestedMessage(payload=InventoryListRequestedPayload(item_type='frozen', name='Corn'), **envelope())

    assert message.event_type == 'public.inventory.list.requested'


def test_updated_message_event_type_and_correlation_id_round_trip():
    fields = envelope()
    message = InventoryListUpdatedMessage(payload=InventoryListUpdatedPayload(), **fields)

    assert message.event_type == 'public.inventory.list.updated'
    assert InventoryListUpdatedMessage.model_validate_json(message.model_dump_json()).correlation_id == fields['correlation_id']
