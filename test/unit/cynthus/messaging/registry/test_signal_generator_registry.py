"""Tests for cynthus.messaging.registry.signal_generator_registry (SignalGeneratorRegistry).

The constructor is taken to accept an iterable of generator classes (spec 4.5 does not give its signature).
"""

import dataclasses

import pytest

from cynthus.core.event import InventoryEvent, InventoryLocationCreatedEvent, InventoryShelfCreatedEvent
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.public_inventory_base import PublicInventorySignalBase
from cynthus.messaging.common.signal.public_inventory_location_created import PublicInventoryLocationCreatedSignal
from cynthus.messaging.common.signal.public_inventory_shelf_created import PublicInventoryShelfCreatedSignal
from cynthus.messaging.component.inventory.generator import (
    InventoryLocationSignalGenerator,
    InventoryShelfSignalGenerator,
)
from cynthus.messaging.component.inventory.message import InventoryShelfCreatedMessage
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.registry import SignalGeneratorRegistry, UnknownEventError
from cynthus.messaging.registry.signal_generator_registry import SignalGeneratorRegistry as Direct

Shelf, Location = InventoryShelfSignalGenerator, InventoryLocationSignalGenerator
SHELF_CONTRACT, LOCATION_CONTRACT = Shelf.contracts[0], Location.contracts[0]


def _generator(contract):
    """A test-only generator holding one contract."""

    class _Generator(SignalGenerator):
        contracts = (contract,)

        def created(self, event):
            raise NotImplementedError

    return _Generator


def _resolved(found):
    """``generator_for`` may hand back the class or an instance; either is a generator of that class."""

    return found if isinstance(found, type) else type(found)


def test_is_exported_from_the_package():
    assert Direct is SignalGeneratorRegistry


class TestBuild:
    def test_empty_registry_has_no_contracts(self):
        assert tuple(SignalGeneratorRegistry([]).contracts()) == ()

    def test_contracts_come_from_the_generators(self):
        registry = SignalGeneratorRegistry([Shelf, Location])

        assert set(registry.contracts()) == set(Shelf.contracts) | set(Location.contracts)
        assert SHELF_CONTRACT in registry.contracts()
        assert LOCATION_CONTRACT in registry.contracts()

    def test_list_is_not_kept_by_reference(self):
        generators = [Shelf]
        registry = SignalGeneratorRegistry(generators)

        generators.append(Location)

        with pytest.raises(UnknownEventError):
            registry.signal_for('InventoryLocationCreatedEvent')

    def test_empty_event_name_is_refused(self):
        contract = dataclasses.replace(SHELF_CONTRACT, event='')

        with pytest.raises(ValueError):
            SignalGeneratorRegistry([_generator(contract)])

    def test_duplicate_event_name_is_refused(self):
        twin = dataclasses.replace(LOCATION_CONTRACT, event=SHELF_CONTRACT.event)

        with pytest.raises(ValueError, match=SHELF_CONTRACT.event):
            SignalGeneratorRegistry([Shelf, _generator(twin)])

    def test_duplicate_signal_name_is_refused(self):
        twin = dataclasses.replace(SHELF_CONTRACT, event='OtherShelfEvent')

        with pytest.raises(ValueError, match=SHELF_CONTRACT.signal.name):
            SignalGeneratorRegistry([Shelf, _generator(twin)])

    def test_same_generator_twice_is_refused(self):
        with pytest.raises(ValueError):
            SignalGeneratorRegistry([Shelf, Shelf])

    def test_failed_register_leaves_the_registry_unchanged(self):
        class _Two(SignalGenerator):
            contracts = (LOCATION_CONTRACT, SHELF_CONTRACT)

            def created(self, event):
                raise NotImplementedError

        registry = SignalGeneratorRegistry([Shelf])

        with pytest.raises(ValueError):
            registry.register(_Two)

        assert len(registry) == len(Shelf.contracts)
        assert registry.event_names() == tuple(sorted(c.event for c in Shelf.contracts))
        assert LOCATION_CONTRACT.event not in registry
        registry.register(Location)
        assert LOCATION_CONTRACT.event in registry

    @pytest.mark.parametrize('bad', [None, 5, 'Shelf', object, int])
    def test_non_generator_is_refused(self, bad):
        with pytest.raises(ValueError):
            SignalGeneratorRegistry([bad])

    def test_signal_name_must_follow_the_naming_rule(self):
        class BadlyNamed(PublicInventorySignalBase):
            aggregate = 'Bad Thing'
            action = SignalActionType.CREATED

        class BadlyNamedMessage(InventoryShelfCreatedMessage):
            event_type: str = BadlyNamed.name

        contract = dataclasses.replace(SHELF_CONTRACT, signal=BadlyNamed, message=BadlyNamedMessage)

        with pytest.raises(ValueError):
            SignalGeneratorRegistry([_generator(contract)])

    def test_an_empty_registry_is_honoured_not_replaced_by_the_default(self):
        registry = SignalGeneratorRegistry([])

        with pytest.raises(UnknownEventError):
            registry.generator_for('InventoryShelfCreatedEvent')


class TestGeneratorFor:
    def test_by_name(self):
        assert _resolved(SignalGeneratorRegistry([Shelf, Location]).generator_for('InventoryShelfCreatedEvent')) is Shelf

    def test_by_instance_uses_the_class_name(self, make_event):
        event = make_event(
            InventoryLocationCreatedEvent, {'location_id': 'l', 'name': 'n', 'type': 'ambient'}
        )

        assert _resolved(SignalGeneratorRegistry([Shelf, Location]).generator_for(event)) is Location

    def test_result_can_generate(self, make_event):
        event = make_event(
            InventoryShelfCreatedEvent, {'shelf_id': 's', 'location_id': 'l', 'name': 'n', 'position': 1}
        )
        found = SignalGeneratorRegistry([Shelf]).generator_for(event)
        generator = found() if isinstance(found, type) else found

        assert generator.generate(event).payload.shelf_id == 's'

    def test_unknown_name(self):
        with pytest.raises(UnknownEventError, match='NopeEvent'):
            SignalGeneratorRegistry([Shelf]).generator_for('NopeEvent')

    def test_unknown_instance_names_the_event_class(self, make_event):
        with pytest.raises(UnknownEventError, match='InventoryEvent'):
            SignalGeneratorRegistry([Shelf]).generator_for(make_event(InventoryEvent, {}))

    def test_subclass_of_a_registered_event_is_not_matched(self, make_event):
        class ChildEvent(InventoryShelfCreatedEvent):
            pass

        event = make_event(ChildEvent, {'shelf_id': 's', 'location_id': 'l', 'name': 'n'})

        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry([Shelf]).generator_for(event)

    def test_empty_string_is_a_miss(self):
        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry([Shelf]).generator_for('')

    def test_lookup_is_case_sensitive(self):
        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry([Shelf]).generator_for('inventoryshelfcreatedevent')

    def test_miss_is_a_lookup_error(self):
        with pytest.raises(LookupError):
            SignalGeneratorRegistry([]).generator_for('AnyEvent')


class TestSignalFor:
    def test_by_name_returns_the_signal_class(self):
        registry = SignalGeneratorRegistry([Shelf, Location])

        assert registry.signal_for('InventoryShelfCreatedEvent') is PublicInventoryShelfCreatedSignal
        assert registry.signal_for('InventoryLocationCreatedEvent') is PublicInventoryLocationCreatedSignal

    def test_by_instance(self, make_event):
        event = make_event(InventoryLocationCreatedEvent, {'location_id': 'l', 'name': 'n', 'type': 'ambient'})

        assert SignalGeneratorRegistry([Location]).signal_for(event) is PublicInventoryLocationCreatedSignal

    def test_unknown_event(self):
        with pytest.raises(UnknownEventError, match='NopeEvent'):
            SignalGeneratorRegistry([Shelf]).signal_for('NopeEvent')


class TestEventNameFor:
    def test_reverse_lookup(self):
        registry = SignalGeneratorRegistry([Shelf, Location])

        assert registry.event_name_for(PublicInventoryShelfCreatedSignal) == 'InventoryShelfCreatedEvent'
        assert registry.event_name_for(PublicInventoryLocationCreatedSignal) == 'InventoryLocationCreatedEvent'

    def test_unknown_signal(self):
        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry([Shelf]).event_name_for(PublicInventoryLocationCreatedSignal)

    def test_empty_registry(self):
        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry([]).event_name_for(PublicInventoryShelfCreatedSignal)


class TestDefault:
    def test_holds_the_shelf_and_location_generators(self):
        registry = SignalGeneratorRegistry.default()

        assert _resolved(registry.generator_for('InventoryShelfCreatedEvent')) is Shelf
        assert _resolved(registry.generator_for('InventoryLocationCreatedEvent')) is Location

    def test_has_the_contracts_of_both_generators(self):
        registry = SignalGeneratorRegistry.default()

        assert set(registry.contracts()) == set(Shelf.contracts) | set(Location.contracts)
        assert len(registry) == 6

    def test_signals_and_reverse_lookup(self):
        registry = SignalGeneratorRegistry.default()

        assert registry.signal_for('InventoryShelfCreatedEvent') is PublicInventoryShelfCreatedSignal
        assert registry.event_name_for(PublicInventoryShelfCreatedSignal) == 'InventoryShelfCreatedEvent'

    def test_is_a_fresh_instance_each_call(self):
        first, second = SignalGeneratorRegistry.default(), SignalGeneratorRegistry.default()

        assert first is not second
        assert isinstance(first, SignalGeneratorRegistry)

    def test_is_a_classmethod(self):
        assert isinstance(SignalGeneratorRegistry.__dict__['default'], classmethod)

    def test_unknown_event(self, make_event):
        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry.default().generator_for(make_event(InventoryEvent, {}))


def _with_contract(contract):
    """A generator whose contracts are swapped in after class creation, past the class-body checks."""

    generator = _generator(SHELF_CONTRACT)
    generator.contracts = (contract,)

    return generator


class TestInvalidContractsAtRegistration:
    @pytest.mark.parametrize('bad', [None, 'public.inventory.shelf.created', 5, object, int])
    def test_signal_is_not_a_signal_class(self, bad):
        generator = _with_contract(dataclasses.replace(SHELF_CONTRACT, signal=bad))

        with pytest.raises(ValueError, match='not a signal class'):
            SignalGeneratorRegistry([generator])

    def test_signal_base_is_abstract(self):
        from cynthus.messaging.common.signal.base import SignalBase

        generator = _with_contract(dataclasses.replace(SHELF_CONTRACT, signal=SignalBase))

        with pytest.raises(ValueError, match='abstract'):
            SignalGeneratorRegistry([generator])

    def test_intermediate_signal_base_is_abstract(self):
        from cynthus.messaging.common.signal.public_inventory_shelf_base import PublicInventoryShelfSignalBase

        generator = _with_contract(dataclasses.replace(SHELF_CONTRACT, signal=PublicInventoryShelfSignalBase))

        with pytest.raises(ValueError, match='abstract'):
            SignalGeneratorRegistry([generator])

    @pytest.mark.parametrize('bad', [None, 5, ''])
    def test_event_name_must_be_a_non_empty_string(self, bad):
        generator = _with_contract(dataclasses.replace(SHELF_CONTRACT, event=bad))

        with pytest.raises(ValueError, match='non-empty'):
            SignalGeneratorRegistry([generator])


class TestContainer:
    def test_contains(self):
        registry = SignalGeneratorRegistry([Shelf])

        assert 'InventoryShelfCreatedEvent' in registry
        assert 'InventoryLocationCreatedEvent' not in registry
        assert '' not in registry

    @pytest.mark.parametrize('other', [None, 5, object(), InventoryShelfCreatedEvent])
    def test_contains_non_str(self, other):
        assert other not in SignalGeneratorRegistry([Shelf])

    def test_len(self):
        assert len(SignalGeneratorRegistry([])) == 0
        assert len(SignalGeneratorRegistry([Shelf])) == 3
        assert len(SignalGeneratorRegistry([Shelf, Location])) == 6

    def test_event_names_are_a_sorted_tuple(self):
        names = SignalGeneratorRegistry([Shelf, Location]).event_names()

        assert names == (
            'InventoryLocationCreatedEvent',
            'InventoryLocationDeletedEvent',
            'InventoryLocationUpdatedEvent',
            'InventoryShelfCreatedEvent',
            'InventoryShelfDeletedEvent',
            'InventoryShelfUpdatedEvent',
        )
        assert isinstance(names, tuple)

    def test_contracts_are_sorted_by_event_name(self):
        contracts = SignalGeneratorRegistry([Shelf, Location]).contracts()

        assert [c.event for c in contracts] == sorted(c.event for c in contracts)

    def test_event_name_for_a_non_signal(self):
        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry([Shelf]).event_name_for([])
