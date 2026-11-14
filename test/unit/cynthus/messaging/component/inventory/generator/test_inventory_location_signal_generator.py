"""Tests for cynthus.messaging.component.inventory.generator.inventory_location_signal_generator."""

import builtins
import re
import socket

import pytest

import cynthus.core.event as core_event
import cynthus.messaging.component.inventory.message as inventory_message
import cynthus.messaging.component.inventory.payload as inventory_payload
from cynthus.core.event import (
    InventoryEvent,
    InventoryLocationCreatedEvent,
)
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.public_inventory_location_created import PublicInventoryLocationCreatedSignal
from cynthus.messaging.component.inventory.generator import InventoryLocationSignalGenerator
from cynthus.messaging.component.inventory.generator.inventory_location_signal_generator import (
    InventoryLocationSignalGenerator as Direct,
)
from cynthus.messaging.component.inventory.message import InventoryLocationCreatedMessage
from cynthus.messaging.component.inventory.payload import InventoryLocationCreatedPayload
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.registry import UnknownEventError

_DATA = {'location_id': 'loc-1', 'name': 'Pantry', 'type': 'ambient'}


@pytest.fixture
def event(make_event):
    return make_event(InventoryLocationCreatedEvent, dict(_DATA))


def test_is_exported_from_the_package():
    assert Direct is InventoryLocationSignalGenerator


def test_is_a_signal_generator():
    assert issubclass(InventoryLocationSignalGenerator, SignalGenerator)


class TestContract:
    def test_one_contract_for_the_location_created_event(self):
        contract = InventoryLocationSignalGenerator().contract('created')

        assert contract.event == 'InventoryLocationCreatedEvent'
        assert contract.signal is PublicInventoryLocationCreatedSignal
        assert contract.message is InventoryLocationCreatedMessage
        assert contract.payload is InventoryLocationCreatedPayload
        assert contract.lifecycle_action is LifecycleAction.CREATED
        assert contract.method == 'created'

    def test_feature_ids_are_well_formed(self):
        contract = InventoryLocationSignalGenerator().contract('created')

        assert contract.features
        assert all(re.fullmatch(r'FT-[A-Z]{2}-\d{3}', feature) for feature in contract.features)

    def test_every_field_comes_from_event_data(self):
        contract = InventoryLocationSignalGenerator().contract('created')

        assert dict(contract.sources) == {
            'location_id': 'data.location_id', 'name': 'data.name', 'type': 'data.type',
        }


class TestGenerate:
    def test_whole_message(self, event):
        message = InventoryLocationSignalGenerator().generate(event)

        assert type(message) is InventoryLocationCreatedMessage
        assert message.event_type == 'public.inventory.location.created'
        assert message.lifecycle_action == LifecycleAction.CREATED
        assert message.tenant_id == event.tenant.id_
        assert message.workspace_id == event.workspace.id_
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.user.id_

    def test_payload_is_copied_from_the_event(self, event):
        payload = InventoryLocationSignalGenerator().generate(event).payload

        assert isinstance(payload, InventoryLocationCreatedPayload)
        assert payload.location_id == 'loc-1'
        assert payload.name == 'Pantry'
        assert payload.type == 'ambient'

    def test_other_event_is_unknown(self, make_event):
        with pytest.raises(UnknownEventError, match='InventoryEvent'):
            InventoryLocationSignalGenerator().generate(make_event(InventoryEvent, {}))

    def test_is_pure(self, event, monkeypatch):
        before = event.model_copy(deep=True)

        def refuse(*args, **kwargs):
            raise AssertionError('no I/O allowed')

        monkeypatch.setattr(socket, 'socket', refuse)
        monkeypatch.setattr(builtins, 'open', refuse)

        InventoryLocationSignalGenerator().generate(event)

        assert event == before


class TestUpdated:
    @pytest.fixture
    def event(self, make_event):
        return make_event(core_event.InventoryLocationUpdatedEvent, {'location_id': 'loc-1', 'name': 'Larder'})

    def test_contract(self):
        contract = InventoryLocationSignalGenerator().contract('updated')

        assert contract.event == 'InventoryLocationUpdatedEvent'
        assert contract.signal.name == 'public.inventory.location.updated'
        assert contract.message is inventory_message.InventoryLocationUpdatedMessage
        assert contract.payload is inventory_payload.InventoryLocationUpdatedPayload
        assert contract.lifecycle_action is LifecycleAction.UPDATED
        assert contract.method == 'updated'
        assert contract.features == ('FT-IM-001',)
        assert dict(contract.sources) == {'location_id': 'data.location_id', 'name': 'data.name', 'type': 'data.type', 'archived': 'data.archived'}

    def test_whole_message(self, event):
        message = InventoryLocationSignalGenerator().generate(event)

        assert type(message) is inventory_message.InventoryLocationUpdatedMessage
        assert message.event_type == 'public.inventory.location.updated'
        assert message.lifecycle_action == LifecycleAction.UPDATED
        assert message.tenant_id == event.tenant.id_
        assert message.workspace_id == event.workspace.id_
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.user.id_
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on

    def test_payload_is_copied_from_the_event(self, event):
        payload = InventoryLocationSignalGenerator().generate(event).payload

        assert isinstance(payload, inventory_payload.InventoryLocationUpdatedPayload)
        assert payload.observed_at == event.occurred_on
        assert payload.location_id == 'loc-1'
        assert payload.name == 'Larder'
        assert payload.type is None
        assert payload.archived is None

    def test_same_event_gives_equal_messages(self, event):
        assert InventoryLocationSignalGenerator().generate(event) == InventoryLocationSignalGenerator().generate(event)

    def test_falsy_values_are_kept_not_dropped(self, make_event):
        event = make_event(core_event.InventoryLocationUpdatedEvent, {'location_id': 'loc-1', 'archived': False})
        payload = InventoryLocationSignalGenerator().generate(event).payload

        assert payload.name is None
        assert payload.type is None
        assert payload.archived is False

    def test_other_event_is_unknown(self, make_event):
        with pytest.raises(UnknownEventError):
            InventoryLocationSignalGenerator().generate(make_event(InventoryEvent, {}))


class TestDeleted:
    @pytest.fixture
    def event(self, make_event):
        return make_event(core_event.InventoryLocationDeletedEvent, {'location_id': 'loc-1'})

    def test_contract(self):
        contract = InventoryLocationSignalGenerator().contract('deleted')

        assert contract.event == 'InventoryLocationDeletedEvent'
        assert contract.signal.name == 'public.inventory.location.deleted'
        assert contract.message is inventory_message.InventoryLocationDeletedMessage
        assert contract.payload is inventory_payload.InventoryLocationDeletedPayload
        assert contract.lifecycle_action is LifecycleAction.DELETED
        assert contract.method == 'deleted'
        assert contract.features == ('FT-IM-001',)
        assert dict(contract.sources) == {'location_id': 'data.location_id'}

    def test_whole_message(self, event):
        message = InventoryLocationSignalGenerator().generate(event)

        assert type(message) is inventory_message.InventoryLocationDeletedMessage
        assert message.event_type == 'public.inventory.location.deleted'
        assert message.lifecycle_action == LifecycleAction.DELETED
        assert message.tenant_id == event.tenant.id_
        assert message.workspace_id == event.workspace.id_
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.user.id_
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on

    def test_payload_is_copied_from_the_event(self, event):
        payload = InventoryLocationSignalGenerator().generate(event).payload

        assert isinstance(payload, inventory_payload.InventoryLocationDeletedPayload)
        assert payload.observed_at == event.occurred_on
        assert payload.location_id == 'loc-1'

    def test_same_event_gives_equal_messages(self, event):
        assert InventoryLocationSignalGenerator().generate(event) == InventoryLocationSignalGenerator().generate(event)

    def test_other_event_is_unknown(self, make_event):
        with pytest.raises(UnknownEventError):
            InventoryLocationSignalGenerator().generate(make_event(InventoryEvent, {}))
