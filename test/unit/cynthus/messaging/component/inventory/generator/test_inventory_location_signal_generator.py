"""Tests for cynthus.messaging.component.inventory.generator.inventory_location_signal_generator."""

import builtins
import re
import socket

import pytest

from cynthus.core.event import InventoryEvent, InventoryLocationCreatedEvent
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
        (contract,) = InventoryLocationSignalGenerator.contracts

        assert contract.event == 'InventoryLocationCreatedEvent'
        assert contract.signal is PublicInventoryLocationCreatedSignal
        assert contract.message is InventoryLocationCreatedMessage
        assert contract.payload is InventoryLocationCreatedPayload
        assert contract.lifecycle_action is LifecycleAction.CREATED
        assert contract.method == 'created'

    def test_feature_ids_are_well_formed(self):
        (contract,) = InventoryLocationSignalGenerator.contracts

        assert contract.features
        assert all(re.fullmatch(r'FT-[A-Z]{2}-\d{3}', feature) for feature in contract.features)

    def test_every_field_comes_from_event_data(self):
        (contract,) = InventoryLocationSignalGenerator.contracts

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
