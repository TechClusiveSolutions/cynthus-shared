"""FEATURE integration (AC9): FT-IM-001 from a real InventoryShelfCreatedEvent to a transport's publish().

No broker is needed: a recording transport stands in for RabbitMQ. The system check (API to broker to the Inventory
service) is a separate follow-up in cynthus-testing.
"""

import pytest

from cynthus.core.event import (
    EventAction,
    InventoryLocationDeletedEvent,
    InventoryLocationUpdatedEvent,
    InventoryShelfCreatedEvent,
    InventoryShelfDeletedEvent,
    InventoryShelfUpdatedEvent,
)
from cynthus.core.resource import StorageLocation
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.component.inventory.message import InventoryShelfCreatedMessage
from cynthus.messaging.component.inventory.payload import InventoryShelfCreatedPayload
from cynthus.messaging.publisher.event_message_publisher import EventMessagePublisher
from cynthus.messaging.publisher.signal_publisher import SignalPublisher

pytestmark = pytest.mark.asyncio


class Recording(SignalPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, message, access_token=None, *, topic=None):
        self.calls.append((message, access_token, topic))


def build(data):
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)
    event = InventoryShelfCreatedEvent(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, action=EventAction.CREATED, data=data,
        user=user,
    )

    return event, user, tenant, workspace


async def test_shelf_created_event_reaches_publish_as_the_whole_message():
    transport = Recording()
    event, user, tenant, workspace = build(
        {'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf', 'position': 3}
    )

    returned = await EventMessagePublisher(transport).publish(event, 'token')

    assert len(transport.calls) == 1

    message, token, topic = transport.calls[0]

    assert returned is message
    assert token == 'token'
    assert topic is None
    assert type(message) is InventoryShelfCreatedMessage
    assert message.event_type == 'public.inventory.shelf.created'
    assert message.lifecycle_action == LifecycleAction.CREATED
    assert message.tenant_id == tenant.id_
    assert message.organization_id == tenant.id_
    assert message.workspace_id == workspace.id_
    assert message.correlation_id == event.correlation_id
    assert message.actor_id == user.id_
    assert isinstance(message.payload, InventoryShelfCreatedPayload)
    assert message.payload.schema_version == 1
    assert message.payload.shelf_id == 'shelf-1'
    assert message.payload.location_id == 'loc-1'
    assert message.payload.name == 'Top shelf'
    assert message.payload.position == 3


async def test_position_defaults_to_zero_all_the_way():
    transport = Recording()
    event, *_ = build({'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf'})

    await EventMessagePublisher(transport).publish(event)

    assert transport.calls[0][0].payload.position == 0


async def test_the_wire_form_carries_the_signal_name_and_payload():
    transport = Recording()
    event, *_ = build({'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf', 'position': 1})

    await EventMessagePublisher(transport).publish(event)

    wire = transport.calls[0][0].model_dump(mode='json')

    assert wire['event_type'] == 'public.inventory.shelf.created'
    assert wire['lifecycle_action'] == 'created'
    assert wire['payload']['shelf_id'] == 'shelf-1'
    assert wire['payload']['position'] == 1


async def test_the_event_is_not_changed_by_publishing():
    transport = Recording()
    event, *_ = build({'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf', 'position': 1})
    before = event.model_copy(deep=True)

    await EventMessagePublisher(transport).publish(event)

    assert event == before


async def test_an_invalid_event_fails_before_any_publish():
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match='shelf_id'):
        build({'location_id': 'loc-1', 'name': 'Top shelf'})


CASES = [
    (InventoryShelfUpdatedEvent, EventAction.UPDATED, {'shelf_id': 's-1', 'location_id': 'l-1', 'name': 'New'},
     'public.inventory.shelf.updated', LifecycleAction.UPDATED,
     {'shelf_id': 's-1', 'location_id': 'l-1', 'name': 'New', 'position': None}),
    (InventoryShelfDeletedEvent, EventAction.DELETED, {'shelf_id': 's-1', 'location_id': 'l-1'},
     'public.inventory.shelf.deleted', LifecycleAction.DELETED, {'shelf_id': 's-1', 'location_id': 'l-1'}),
    (InventoryLocationUpdatedEvent, EventAction.UPDATED, {'location_id': 'l-1', 'archived': True},
     'public.inventory.location.updated', LifecycleAction.UPDATED,
     {'location_id': 'l-1', 'name': None, 'type': None, 'archived': True}),
    (InventoryLocationDeletedEvent, EventAction.DELETED, {'location_id': 'l-1'},
     'public.inventory.location.deleted', LifecycleAction.DELETED, {'location_id': 'l-1'}),
]


@pytest.mark.parametrize(('event_class', 'action', 'data', 'signal_name', 'lifecycle', 'payload'), CASES)
async def test_updated_and_deleted_events_reach_publish_as_the_whole_message(
    event_class, action, data, signal_name, lifecycle, payload
):
    transport = Recording()
    user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
    tenant = Tenant(name='T00001', owner=user, type='personal')
    workspace = Workspace(name='W00001', tenant=tenant, owner=user)
    location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)
    event = event_class(
        name='E0001', tenant=tenant, workspace=workspace, resource=location, action=action, data=data, user=user
    )

    returned = await EventMessagePublisher(transport).publish(event, 'token')

    (message, token, topic), = transport.calls

    assert returned is message
    assert (token, topic) == ('token', None)
    assert message.event_type == signal_name
    assert message.lifecycle_action == lifecycle
    assert message.event_id == event.id_
    assert message.timestamp == event.occurred_on
    assert message.tenant_id == tenant.id_
    assert message.workspace_id == workspace.id_
    assert message.correlation_id == event.correlation_id
    assert message.actor_id == user.id_
    assert message.payload.observed_at == event.occurred_on

    for field, value in payload.items():
        assert getattr(message.payload, field) == value
