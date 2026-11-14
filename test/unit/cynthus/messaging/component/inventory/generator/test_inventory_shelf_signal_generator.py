"""Tests for cynthus.messaging.component.inventory.generator.inventory_shelf_signal_generator."""

import builtins
import re
import socket

import pytest

import cynthus.core.event as core_event
import cynthus.messaging.component.inventory.message as inventory_message
import cynthus.messaging.component.inventory.payload as inventory_payload
from cynthus.core.event import InventoryEvent, InventoryShelfCreatedEvent
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.public_inventory_shelf_created import PublicInventoryShelfCreatedSignal
from cynthus.messaging.component.inventory.generator import InventoryShelfSignalGenerator
from cynthus.messaging.component.inventory.generator.inventory_shelf_signal_generator import (
    InventoryShelfSignalGenerator as Direct,
)
from cynthus.messaging.component.inventory.message import InventoryShelfCreatedMessage
from cynthus.messaging.component.inventory.payload import InventoryShelfCreatedPayload
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.registry import UnknownEventError

_DATA = {'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf', 'position': 4}


@pytest.fixture
def event(make_event):
    return make_event(InventoryShelfCreatedEvent, dict(_DATA))


def test_is_exported_from_the_package():
    assert Direct is InventoryShelfSignalGenerator


def test_is_a_signal_generator():
    assert issubclass(InventoryShelfSignalGenerator, SignalGenerator)


class TestContract:
    def test_one_contract_for_the_shelf_created_event(self):
        contract = InventoryShelfSignalGenerator().contract('created')

        assert contract.event == 'InventoryShelfCreatedEvent'
        assert contract.signal is PublicInventoryShelfCreatedSignal
        assert contract.message is InventoryShelfCreatedMessage
        assert contract.payload is InventoryShelfCreatedPayload
        assert contract.lifecycle_action is LifecycleAction.CREATED
        assert contract.method == 'created'

    def test_feature_is_ft_im_001(self):
        contract = InventoryShelfSignalGenerator().contract('created')

        assert 'FT-IM-001' in contract.features
        assert all(re.fullmatch(r'FT-[A-Z]{2}-\d{3}', feature) for feature in contract.features)

    def test_every_field_comes_from_event_data(self):
        contract = InventoryShelfSignalGenerator().contract('created')

        assert dict(contract.sources) == {
            'shelf_id': 'data.shelf_id', 'location_id': 'data.location_id', 'name': 'data.name',
            'position': 'data.position',
        }

    def test_the_method_exists(self):
        assert callable(getattr(InventoryShelfSignalGenerator, 'created'))


class TestGenerate:
    def test_whole_message(self, event):
        message = InventoryShelfSignalGenerator().generate(event)

        assert type(message) is InventoryShelfCreatedMessage
        assert message.event_type == 'public.inventory.shelf.created'
        assert message.lifecycle_action == LifecycleAction.CREATED
        assert message.tenant_id == event.tenant.id_
        assert message.workspace_id == event.workspace.id_
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.user.id_

    def test_payload_is_copied_from_the_event(self, event):
        payload = InventoryShelfSignalGenerator().generate(event).payload

        assert isinstance(payload, InventoryShelfCreatedPayload)
        assert payload.shelf_id == 'shelf-1'
        assert payload.location_id == 'loc-1'
        assert payload.name == 'Top shelf'
        assert payload.position == 4

    def test_position_defaults_to_zero(self, make_event):
        data = {key: value for key, value in _DATA.items() if key != 'position'}

        payload = InventoryShelfSignalGenerator().generate(make_event(InventoryShelfCreatedEvent, data)).payload

        assert payload.position == 0

    def test_explicit_zero_position_stays_zero(self, make_event):
        event = make_event(InventoryShelfCreatedEvent, {**_DATA, 'position': 0})

        assert InventoryShelfSignalGenerator().generate(event).payload.position == 0

    def test_other_event_is_unknown(self, make_event):
        with pytest.raises(UnknownEventError, match='InventoryEvent'):
            InventoryShelfSignalGenerator().generate(make_event(InventoryEvent, {}))

    def test_is_pure(self, event, monkeypatch):
        before = event.model_copy(deep=True)

        def refuse(*args, **kwargs):
            raise AssertionError('no I/O allowed')

        monkeypatch.setattr(socket, 'socket', refuse)
        monkeypatch.setattr(builtins, 'open', refuse)

        InventoryShelfSignalGenerator().generate(event)

        assert event == before


class TestUpdated:
    @pytest.fixture
    def event(self, make_event):
        return make_event(core_event.InventoryShelfUpdatedEvent, {'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'New name'})

    def test_contract(self):
        contract = InventoryShelfSignalGenerator().contract('updated')

        assert contract.event == 'InventoryShelfUpdatedEvent'
        assert contract.signal.name == 'public.inventory.shelf.updated'
        assert contract.message is inventory_message.InventoryShelfUpdatedMessage
        assert contract.payload is inventory_payload.InventoryShelfUpdatedPayload
        assert contract.lifecycle_action is LifecycleAction.UPDATED
        assert contract.method == 'updated'
        assert contract.features == ('FT-IM-001',)
        assert dict(contract.sources) == {'shelf_id': 'data.shelf_id', 'location_id': 'data.location_id', 'name': 'data.name', 'position': 'data.position'}

    def test_whole_message(self, event):
        message = InventoryShelfSignalGenerator().generate(event)

        assert type(message) is inventory_message.InventoryShelfUpdatedMessage
        assert message.event_type == 'public.inventory.shelf.updated'
        assert message.lifecycle_action == LifecycleAction.UPDATED
        assert message.tenant_id == event.tenant.id_
        assert message.workspace_id == event.workspace.id_
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.user.id_
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on

    def test_payload_is_copied_from_the_event(self, event):
        payload = InventoryShelfSignalGenerator().generate(event).payload

        assert isinstance(payload, inventory_payload.InventoryShelfUpdatedPayload)
        assert payload.observed_at == event.occurred_on
        assert payload.shelf_id == 'shelf-1'
        assert payload.location_id == 'loc-1'
        assert payload.name == 'New name'
        assert payload.position is None

    def test_same_event_gives_equal_messages(self, event):
        assert InventoryShelfSignalGenerator().generate(event) == InventoryShelfSignalGenerator().generate(event)

    def test_falsy_values_are_kept_not_dropped(self, make_event):
        event = make_event(core_event.InventoryShelfUpdatedEvent, {'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'position': 0})
        payload = InventoryShelfSignalGenerator().generate(event).payload

        assert payload.name is None
        assert payload.position == 0

    def test_other_event_is_unknown(self, make_event):
        with pytest.raises(UnknownEventError):
            InventoryShelfSignalGenerator().generate(make_event(InventoryEvent, {}))


class TestDeleted:
    @pytest.fixture
    def event(self, make_event):
        return make_event(core_event.InventoryShelfDeletedEvent, {'shelf_id': 'shelf-1', 'location_id': 'loc-1'})

    def test_contract(self):
        contract = InventoryShelfSignalGenerator().contract('deleted')

        assert contract.event == 'InventoryShelfDeletedEvent'
        assert contract.signal.name == 'public.inventory.shelf.deleted'
        assert contract.message is inventory_message.InventoryShelfDeletedMessage
        assert contract.payload is inventory_payload.InventoryShelfDeletedPayload
        assert contract.lifecycle_action is LifecycleAction.DELETED
        assert contract.method == 'deleted'
        assert contract.features == ('FT-IM-001',)
        assert dict(contract.sources) == {'shelf_id': 'data.shelf_id', 'location_id': 'data.location_id'}

    def test_whole_message(self, event):
        message = InventoryShelfSignalGenerator().generate(event)

        assert type(message) is inventory_message.InventoryShelfDeletedMessage
        assert message.event_type == 'public.inventory.shelf.deleted'
        assert message.lifecycle_action == LifecycleAction.DELETED
        assert message.tenant_id == event.tenant.id_
        assert message.workspace_id == event.workspace.id_
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.user.id_
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on

    def test_payload_is_copied_from_the_event(self, event):
        payload = InventoryShelfSignalGenerator().generate(event).payload

        assert isinstance(payload, inventory_payload.InventoryShelfDeletedPayload)
        assert payload.observed_at == event.occurred_on
        assert payload.shelf_id == 'shelf-1'
        assert payload.location_id == 'loc-1'

    def test_same_event_gives_equal_messages(self, event):
        assert InventoryShelfSignalGenerator().generate(event) == InventoryShelfSignalGenerator().generate(event)

    def test_other_event_is_unknown(self, make_event):
        with pytest.raises(UnknownEventError):
            InventoryShelfSignalGenerator().generate(make_event(InventoryEvent, {}))
