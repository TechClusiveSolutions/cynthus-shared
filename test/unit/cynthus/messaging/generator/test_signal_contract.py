"""Tests for cynthus.messaging.generator.signal_contract (SignalContract)."""

import dataclasses

import pytest

from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.public_inventory_shelf_created import PublicInventoryShelfCreatedSignal
from cynthus.messaging.component.inventory.message import InventoryShelfCreatedMessage
from cynthus.messaging.component.inventory.payload import InventoryShelfCreatedPayload
from cynthus.messaging.generator.signal_contract import SignalContract

_SOURCES = {
    'shelf_id': 'data.shelf_id',
    'location_id': 'data.location_id',
    'name': 'data.name',
    'position': 'data.position',
}


def _contract(**overrides):
    values = {
        'features': ('FT-IM-001',),
        'event': 'InventoryShelfCreatedEvent',
        'signal': PublicInventoryShelfCreatedSignal,
        'message': InventoryShelfCreatedMessage,
        'payload': InventoryShelfCreatedPayload,
        'lifecycle_action': LifecycleAction.CREATED,
        'method': 'created',
        'sources': dict(_SOURCES),
    }

    return SignalContract(**{**values, **overrides})


def test_is_a_dataclass():
    assert dataclasses.is_dataclass(SignalContract)


def test_field_names():
    assert [field.name for field in dataclasses.fields(SignalContract)] == [
        'features', 'event', 'signal', 'message', 'payload', 'lifecycle_action', 'method', 'sources',
    ]


def test_values_are_kept():
    contract = _contract()

    assert contract.features == ('FT-IM-001',)
    assert contract.event == 'InventoryShelfCreatedEvent'
    assert contract.signal is PublicInventoryShelfCreatedSignal
    assert contract.message is InventoryShelfCreatedMessage
    assert contract.payload is InventoryShelfCreatedPayload
    assert contract.lifecycle_action is LifecycleAction.CREATED
    assert contract.method == 'created'
    assert dict(contract.sources) == _SOURCES


def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        _contract().method = 'other'


@pytest.mark.parametrize('name', ['features', 'event', 'signal', 'message', 'payload', 'lifecycle_action', 'method',
                                  'sources'])
def test_every_field_is_required(name):
    values = {
        'features': ('FT-IM-001',), 'event': 'E', 'signal': PublicInventoryShelfCreatedSignal,
        'message': InventoryShelfCreatedMessage, 'payload': InventoryShelfCreatedPayload,
        'lifecycle_action': LifecycleAction.CREATED, 'method': 'created', 'sources': {},
    }
    del values[name]

    with pytest.raises(TypeError):
        SignalContract(**values)


def test_equal_contracts_compare_equal():
    assert _contract() == _contract()


def test_different_contracts_compare_unequal():
    assert _contract() != _contract(method='updated')


def test_several_features_are_allowed():
    assert _contract(features=('FT-IM-001', 'FT-IM-002')).features == ('FT-IM-001', 'FT-IM-002')
