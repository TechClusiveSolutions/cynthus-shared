"""Drift tests (AC8): every contract in the default registry stays consistent with the events, signals and messages it
names. They live under test/integration because each check spans core events, messaging and the registry."""

import re

import pytest

import cynthus.core.event as core_event
from cynthus.core.event import Event
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.payload import SignalPayload
from cynthus.messaging.generator.signal_contract import SignalContract
from cynthus.messaging.registry import SignalGeneratorRegistry

_CONTRACTS = tuple(SignalGeneratorRegistry.default().contracts())
_IDS = [contract.event for contract in _CONTRACTS]
_SIGNAL_NAME = re.compile(r'^[a-z]+(\.[a-z_]+){3}$')
_FEATURE = re.compile(r'^FT-[A-Z]{2}-\d{3}$')
_SOURCE_KINDS = ('data', 'resource', 'user', 'tenant', 'workspace', 'env')
_SOURCE = re.compile(r'^((data|resource|user|tenant|workspace)\.[a-z_][a-z0-9_]*|env\.[A-Za-z_][A-Za-z0-9_]*)$')
_LIFECYCLE = {a.value: a for a in LifecycleAction}
_BASE_FIELDS = set(SignalPayload.model_fields)


def test_the_default_registry_is_not_empty():
    assert _CONTRACTS


def test_every_item_is_a_contract():
    assert all(isinstance(contract, SignalContract) for contract in _CONTRACTS)


def test_signal_names_are_unique():
    names = [contract.signal.name for contract in _CONTRACTS]

    assert len(names) == len(set(names))


def test_event_names_are_unique():
    assert len(_IDS) == len(set(_IDS))


@pytest.mark.parametrize('contract', _CONTRACTS, ids=_IDS)
class TestContract:
    def test_signal_is_a_concrete_signal_with_a_valid_name(self, contract):
        assert isinstance(contract.signal, type)
        assert issubclass(contract.signal, SignalBase)
        assert _SIGNAL_NAME.fullmatch(contract.signal.name), contract.signal.name

    def test_message_default_event_type_is_the_signal_name(self, contract):
        assert contract.message.model_fields['event_type'].default == contract.signal.name

    def test_payload_is_the_message_payload_type(self, contract):
        assert contract.message.model_fields['payload'].annotation is contract.payload

    def test_every_payload_field_has_a_source(self, contract):
        fields = set(contract.payload.model_fields) - _BASE_FIELDS

        assert fields
        assert fields <= set(contract.sources), f'no source for {sorted(fields - set(contract.sources))}'

    def test_every_source_names_a_payload_field(self, contract):
        assert set(contract.sources) <= set(contract.payload.model_fields)

    def test_every_source_expression_is_known(self, contract):
        for field, expression in contract.sources.items():
            kind, _, name = expression.partition('.')

            assert kind in _SOURCE_KINDS, f'{field}: {expression}'
            assert name, f'{field}: {expression}'

    def test_every_data_source_exists_on_the_event_data_model(self, contract):
        event_class = getattr(core_event, contract.event)
        data_sources = [e.partition('.')[2] for e in contract.sources.values() if e.startswith('data.')]

        if data_sources:
            assert event_class.data_model is not None, f'{contract.event} has no data_model'
            assert set(data_sources) <= set(event_class.data_model.model_fields)

    def test_features_are_well_formed(self, contract):
        assert contract.features
        assert all(_FEATURE.fullmatch(feature) for feature in contract.features)

    def test_event_class_exists_in_core_event(self, contract):
        event_class = getattr(core_event, contract.event, None)

        assert isinstance(event_class, type), f'{contract.event} is not exported from cynthus.core.event'
        assert issubclass(event_class, Event)
        assert event_class.__name__ == contract.event

    def test_event_type_matches_the_signal_name(self, contract):
        event_type = getattr(core_event, contract.event).model_construct().event_type
        expected = contract.signal.name.split('.', 1)[1].replace('.', '_')

        assert event_type == expected

    def test_method_exists_on_a_registered_generator(self, contract):
        generator = SignalGeneratorRegistry.default().generator_for(contract.event)

        assert callable(getattr(type(generator), contract.method))

    def test_round_trip_through_the_registry(self, contract):
        registry = SignalGeneratorRegistry.default()

        assert registry.signal_for(contract.event) is contract.signal
        assert registry.event_name_for(contract.signal) == contract.event

    def test_every_source_matches_the_expression_format(self, contract):
        for field, expression in contract.sources.items():
            assert _SOURCE.fullmatch(expression), f'{field}: {expression}'

    def test_lifecycle_action_agrees_with_the_signal_action(self, contract):
        action = contract.signal.action.value

        if action in _LIFECYCLE:
            assert contract.lifecycle_action is _LIFECYCLE[action]
