"""Tests for cynthus.messaging.generator.signal_generator (SignalGenerator).

The generator is exercised through small test-only subclasses so the base is tested apart from the real resource
generators. Events are real events built through the ``make_event`` fixture.
"""

import builtins
import dataclasses
import socket
from uuid import UUID, uuid4

import pytest

from cynthus.core.event import Event, EventAction, InventoryShelfCreatedEvent, SignalEvent, SystemEvent
from cynthus.core.system.system import SYSTEM_ID
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.public_inventory_location_created import PublicInventoryLocationCreatedSignal
from cynthus.messaging.common.signal.public_inventory_shelf_created import PublicInventoryShelfCreatedSignal
from cynthus.messaging.component.inventory.message import InventoryLocationCreatedMessage, InventoryShelfCreatedMessage
from cynthus.messaging.component.inventory.payload import InventoryLocationCreatedPayload, InventoryShelfCreatedPayload
from cynthus.messaging.generator.signal_contract import SignalContract
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.registry import UnknownEventError

_SHELF_DATA = {'shelf_id': 'shelf-1', 'location_id': 'loc-1', 'name': 'Top shelf', 'position': 4}

SHELF = SignalContract(
    features=('FT-IM-001',),
    event='InventoryShelfCreatedEvent',
    signal=PublicInventoryShelfCreatedSignal,
    message=InventoryShelfCreatedMessage,
    payload=InventoryShelfCreatedPayload,
    lifecycle_action=LifecycleAction.CREATED,
    method='created',
    sources={
        'shelf_id': 'data.shelf_id', 'location_id': 'data.location_id', 'name': 'data.name',
        'position': 'data.position',
    },
)

LOCATION = SignalContract(
    features=('FT-IM-001',),
    event='InventoryLocationCreatedEvent',
    signal=PublicInventoryLocationCreatedSignal,
    message=InventoryLocationCreatedMessage,
    payload=InventoryLocationCreatedPayload,
    lifecycle_action=LifecycleAction.CREATED,
    method='location_created',
    sources={'location_id': 'data.location_id', 'name': 'data.name', 'type': 'data.type'},
)


class SysShelfEvent(SystemEvent):
    """A system-made shelf event (no user)"""


class NobodyShelfEvent(Event):
    """An event with neither a user nor a system"""


def _build(contract, event_name=None):
    """A test-only generator for one contract; its ``created`` method fills only the body."""

    contract = dataclasses.replace(contract, event=event_name or contract.event, method='created')

    class _Generator(SignalGenerator):
        contracts = (contract,)

        def created(self, event):
            payload = contract.payload(**event.data, observed_at=event.occurred_on)

            return contract.message(**self.envelope(event, contract), payload=payload)

    return _Generator


class _ShelfGenerator(SignalGenerator):
    contracts = (SHELF,)
    seen = []

    def created(self, event):
        type(self).seen.append(event)
        payload = SHELF.payload(**event.data, observed_at=event.occurred_on)

        return SHELF.message(**self.envelope(event, SHELF), payload=payload)


@pytest.fixture
def shelf_event(make_event):
    return make_event(InventoryShelfCreatedEvent, dict(_SHELF_DATA))


class TestGenerate:
    def test_returns_the_contract_message_type(self, shelf_event):
        message = _ShelfGenerator().generate(shelf_event)

        assert type(message) is InventoryShelfCreatedMessage

    def test_whole_message(self, shelf_event):
        message = _ShelfGenerator().generate(shelf_event)

        assert message.event_type == 'public.inventory.shelf.created'
        assert message.lifecycle_action == LifecycleAction.CREATED
        assert message.tenant_id == shelf_event.tenant.id_
        assert message.workspace_id == shelf_event.workspace.id_
        assert message.correlation_id == shelf_event.correlation_id
        assert message.actor_id == shelf_event.user.id_
        assert message.payload.shelf_id == 'shelf-1'
        assert message.payload.location_id == 'loc-1'
        assert message.payload.name == 'Top shelf'
        assert message.payload.position == 4

    def test_message_event_type_is_the_signal_name_not_the_event_type(self, shelf_event):
        message = _ShelfGenerator().generate(shelf_event)

        assert shelf_event.event_type == 'inventory_shelf_created'
        assert message.event_type != shelf_event.event_type
        assert message.event_type == SHELF.signal.name

    def test_calls_the_contract_method_with_the_event(self, shelf_event):
        _ShelfGenerator.seen = []

        _ShelfGenerator().generate(shelf_event)

        assert _ShelfGenerator.seen == [shelf_event]
        assert _ShelfGenerator.seen[0] is shelf_event

    def test_position_defaults_to_zero(self, make_event):
        data = {key: value for key, value in _SHELF_DATA.items() if key != 'position'}

        message = _ShelfGenerator().generate(make_event(InventoryShelfCreatedEvent, data))

        assert message.payload.position == 0

    def test_unknown_event_raises_unknown_event_error(self, make_event):
        event = make_event(SysShelfEvent, dict(_SHELF_DATA))

        with pytest.raises(UnknownEventError, match='SysShelfEvent'):
            _ShelfGenerator().generate(event)

    def test_subclass_of_a_known_event_is_not_matched(self, make_event):
        class ChildShelfEvent(InventoryShelfCreatedEvent):
            pass

        with pytest.raises(UnknownEventError, match='ChildShelfEvent'):
            _ShelfGenerator().generate(make_event(ChildShelfEvent, dict(_SHELF_DATA)))

    def test_picks_the_contract_by_event_name(self, make_event):
        class Two(SignalGenerator):
            contracts = (SHELF, LOCATION)

            def created(self, event):
                payload = SHELF.payload(**event.data, observed_at=event.occurred_on)

                return SHELF.message(**self.envelope(event, SHELF), payload=payload)

            def location_created(self, event):
                payload = LOCATION.payload(**event.data, observed_at=event.occurred_on)

                return LOCATION.message(**self.envelope(event, LOCATION), payload=payload)

        from cynthus.core.event import InventoryLocationCreatedEvent

        location = make_event(
            InventoryLocationCreatedEvent, {'location_id': 'loc-9', 'name': 'Pantry', 'type': 'ambient'}
        )

        assert type(Two().generate(location)) is InventoryLocationCreatedMessage
        assert type(Two().generate(make_event(InventoryShelfCreatedEvent, dict(_SHELF_DATA)))) is (
            InventoryShelfCreatedMessage
        )


class TestEnvelope:
    def test_values_for_a_user_event(self, shelf_event):
        envelope = _ShelfGenerator().envelope(shelf_event, SHELF)

        assert envelope['tenant_id'] == shelf_event.tenant.id_
        assert envelope['workspace_id'] == shelf_event.workspace.id_
        assert envelope['correlation_id'] == shelf_event.correlation_id
        assert envelope['actor_id'] == shelf_event.user.id_
        assert envelope['event_type'] == 'public.inventory.shelf.created'
        assert envelope['lifecycle_action'] == LifecycleAction.CREATED

    def test_lifecycle_action_comes_from_the_contract_not_the_event_action(self, shelf_event):
        contract = dataclasses.replace(SHELF, lifecycle_action=LifecycleAction.UPDATED)

        assert _ShelfGenerator().envelope(shelf_event, contract)['lifecycle_action'] == LifecycleAction.UPDATED

    def test_event_type_comes_from_the_contract_signal(self, shelf_event):
        assert _ShelfGenerator().envelope(shelf_event, LOCATION)['event_type'] == 'public.inventory.location.created'

    def test_actor_is_the_user_for_a_user_event(self, shelf_event):
        actor = _ShelfGenerator().envelope(shelf_event, SHELF)['actor_id']

        assert actor == shelf_event.user.id_
        assert actor != SYSTEM_ID

    def test_actor_is_the_system_for_a_system_event(self, make_event):
        event = make_event(SysShelfEvent, dict(_SHELF_DATA))
        generator = _build(SHELF, 'SysShelfEvent')()

        assert generator.envelope(event, SHELF)['actor_id'] == event.system.id_
        assert generator.generate(event).actor_id == event.system.id_

    def test_actor_of_a_system_event_is_not_a_user_id(self, make_event):
        event = make_event(SysShelfEvent, dict(_SHELF_DATA))

        assert not hasattr(event, 'user')
        assert _build(SHELF, 'SysShelfEvent')().generate(event).actor_id == SYSTEM_ID

    def test_actor_follows_the_event_kind_not_a_fixed_attribute(self, make_event):
        user_event = make_event(InventoryShelfCreatedEvent, dict(_SHELF_DATA))
        system_event = make_event(SysShelfEvent, dict(_SHELF_DATA))
        generator = _build(SHELF, 'SysShelfEvent')()

        assert generator.envelope(system_event, SHELF)['actor_id'] != user_event.user.id_

    def test_event_with_neither_user_nor_system_raises_value_error_naming_the_class(self, make_event):
        event = make_event(NobodyShelfEvent, dict(_SHELF_DATA))
        generator = _build(SHELF, 'NobodyShelfEvent')()

        with pytest.raises(ValueError, match='NobodyShelfEvent'):
            generator.envelope(event, SHELF)

    def test_event_with_neither_fails_generate_with_value_error(self, make_event):
        event = make_event(NobodyShelfEvent, dict(_SHELF_DATA))

        with pytest.raises(ValueError, match='NobodyShelfEvent'):
            _build(SHELF, 'NobodyShelfEvent')().generate(event)

    def test_ids_are_uuids(self, shelf_event):
        envelope = _ShelfGenerator().envelope(shelf_event, SHELF)

        for key in ('tenant_id', 'workspace_id', 'correlation_id', 'actor_id'):
            assert isinstance(envelope[key], UUID)


class TestPurity:
    def test_event_is_unchanged_after_generate(self, shelf_event):
        before = shelf_event.model_copy(deep=True)
        data_before = dict(shelf_event.data)

        _ShelfGenerator().generate(shelf_event)

        assert shelf_event == before
        assert shelf_event.data == data_before
        assert shelf_event.model_dump() == before.model_dump()

    def test_generating_twice_gives_equal_messages(self, shelf_event):
        assert _ShelfGenerator().generate(shelf_event) == _ShelfGenerator().generate(shelf_event)

    def test_no_network_and_no_files(self, shelf_event, monkeypatch):
        def refuse(*args, **kwargs):
            raise AssertionError('a generator must not do I/O')

        monkeypatch.setattr(socket, 'socket', refuse)
        monkeypatch.setattr(socket, 'create_connection', refuse)
        monkeypatch.setattr(socket, 'getaddrinfo', refuse)
        monkeypatch.setattr(builtins, 'open', refuse)

        message = _ShelfGenerator().generate(shelf_event)

        assert message.payload.shelf_id == 'shelf-1'


class TestClassBodyValidation:
    def test_valid_subclass_is_accepted(self):
        assert _build(SHELF)

    def test_two_distinct_contracts_are_accepted(self):
        class Two(SignalGenerator):
            contracts = (SHELF, LOCATION)

            def created(self, event):
                raise NotImplementedError

            def location_created(self, event):
                raise NotImplementedError

        assert len(Two.contracts) == 2

    def test_missing_method(self):
        with pytest.raises(TypeError, match='created'):
            class Broken(SignalGenerator):
                contracts = (SHELF,)

    def test_method_name_is_taken_from_the_contract(self):
        contract = dataclasses.replace(SHELF, method='renamed')

        with pytest.raises(TypeError, match='renamed'):
            class Broken(SignalGenerator):
                contracts = (contract,)

                def created(self, event):
                    raise NotImplementedError

    def test_message_default_event_type_must_equal_the_signal_name(self):
        contract = dataclasses.replace(SHELF, message=InventoryLocationCreatedMessage)

        with pytest.raises(TypeError, match='event_type'):
            class Broken(SignalGenerator):
                contracts = (contract,)

                def created(self, event):
                    raise NotImplementedError

    def test_payload_field_without_a_source(self):
        sources = {key: value for key, value in SHELF.sources.items() if key != 'position'}
        contract = dataclasses.replace(SHELF, sources=sources)

        with pytest.raises(TypeError, match='position'):
            class Broken(SignalGenerator):
                contracts = (contract,)

                def created(self, event):
                    raise NotImplementedError

    def test_two_contracts_for_one_event(self):
        second = dataclasses.replace(LOCATION, event=SHELF.event)

        with pytest.raises(TypeError, match=SHELF.event):
            class Broken(SignalGenerator):
                contracts = (SHELF, second)

                def created(self, event):
                    raise NotImplementedError

                def location_created(self, event):
                    raise NotImplementedError

    def test_two_contracts_for_one_signal_name(self):
        second = dataclasses.replace(SHELF, event='OtherShelfEvent', method='other')

        with pytest.raises(TypeError, match=SHELF.signal.name):
            class Broken(SignalGenerator):
                contracts = (SHELF, second)

                def created(self, event):
                    raise NotImplementedError

                def other(self, event):
                    raise NotImplementedError


class TestDeterminism:
    def test_equal_messages_and_event_values(self, shelf_event):
        first, second = _ShelfGenerator().generate(shelf_event), _ShelfGenerator().generate(shelf_event)

        assert first == second
        assert first.event_id == shelf_event.id_
        assert first.timestamp == shelf_event.occurred_on
        assert first.payload.observed_at == shelf_event.occurred_on

    def test_system_event(self, make_event):
        event = make_event(SysShelfEvent, dict(_SHELF_DATA))
        generator = _build(SHELF, 'SysShelfEvent')()

        message = generator.generate(event)

        assert message == generator.generate(event)
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on

    def test_envelope_carries_id_and_time_of_the_event(self, shelf_event):
        envelope = _ShelfGenerator().envelope(shelf_event, SHELF)

        assert envelope['event_id'] == shelf_event.id_
        assert envelope['timestamp'] == shelf_event.occurred_on


class TestContractLookup:
    def test_finds_by_method_name(self):
        assert _ShelfGenerator().contract('created') is SHELF

    def test_unknown_method(self):
        with pytest.raises(LookupError, match='_ShelfGenerator has no contract for the method nope'):
            _ShelfGenerator().contract('nope')

    def test_two_contracts_with_created_not_first(self, make_event):
        from cynthus.core.event import InventoryLocationCreatedEvent

        class Two(SignalGenerator):
            contracts = (dataclasses.replace(LOCATION, method='location_created'), dataclasses.replace(SHELF))

            def location_created(self, event):
                contract = self.contract('location_created')

                return contract.message(**self.envelope(event, contract), payload=contract.payload(**event.data))

            def created(self, event):
                contract = self.contract('created')

                return contract.message(**self.envelope(event, contract), payload=contract.payload(**event.data))

        assert Two.contracts[0].method == 'location_created'
        assert Two().contract('created').signal is PublicInventoryShelfCreatedSignal
        assert Two().contract('location_created').signal is PublicInventoryLocationCreatedSignal

        shelf = Two().generate(make_event(InventoryShelfCreatedEvent, dict(_SHELF_DATA)))
        location = Two().generate(
            make_event(InventoryLocationCreatedEvent, {'location_id': 'l', 'name': 'n', 'type': 'ambient'})
        )

        assert shelf.event_type == 'public.inventory.shelf.created'
        assert location.event_type == 'public.inventory.location.created'


def _define(contract):
    class Gen(SignalGenerator):
        contracts = (contract,)

        def created(self, event):
            raise NotImplementedError

    return Gen


class TestNewClassBodyChecks:
    def test_source_for_a_field_the_payload_lacks(self):
        contract = dataclasses.replace(SHELF, sources={**SHELF.sources, 'bogus': 'data.bogus'})

        with pytest.raises(TypeError, match='bogus'):
            _define(contract)

    @pytest.mark.parametrize('bad', ['', 'name', 'data.', 'data.Name', 'other.name', 'env.', 'env.A-B', 'data.a.b'])
    def test_malformed_source(self, bad):
        contract = dataclasses.replace(SHELF, sources={**SHELF.sources, 'name': bad})

        with pytest.raises(TypeError, match='malformed source'):
            _define(contract)

    @pytest.mark.parametrize(
        'good', ['data.name', 'resource.id_', 'user.id_', 'tenant.id_', 'workspace.id_', 'env.SERVICE_NAME', 'env.region']
    )
    def test_well_formed_source(self, good):
        contract = dataclasses.replace(SHELF, sources={**SHELF.sources, 'name': good})

        assert _define(contract)

    def test_lifecycle_action_must_match_the_signal_action(self):
        contract = dataclasses.replace(SHELF, lifecycle_action=LifecycleAction.UPDATED)

        with pytest.raises(TypeError, match='lifecycle action'):
            _define(contract)

    def test_matching_lifecycle_action_is_accepted(self):
        assert _define(SHELF)

    def test_signal_action_outside_the_lifecycle_values_is_not_compared(self):
        from cynthus.messaging.common.signal.public_inventory_shelf_requested import (
            PublicInventoryShelfRequestedSignal,
        )

        assert PublicInventoryShelfRequestedSignal.action.value not in {a.value for a in LifecycleAction}

        class Message(InventoryShelfCreatedMessage):
            event_type: str = PublicInventoryShelfRequestedSignal.name

        contract = dataclasses.replace(
            SHELF, signal=PublicInventoryShelfRequestedSignal, message=Message, lifecycle_action=LifecycleAction.CREATED
        )

        assert _define(contract)


class ProbeSignalEvent(SignalEvent):
    """A signal event (ids only) for the shelf contract"""


class TestEnvelopeForSignalEvent:
    @pytest.fixture
    def signal_event(self):
        return ProbeSignalEvent(
            tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=EventAction.CREATED,
            data=dict(_SHELF_DATA),
        )

    def test_carries_the_ids_and_the_contract_values(self, signal_event):
        envelope = _build(SHELF, 'ProbeSignalEvent')().envelope(signal_event, SHELF)

        assert envelope == {
            'event_id': signal_event.id_,
            'timestamp': signal_event.occurred_on,
            'tenant_id': signal_event.tenant_id,
            'workspace_id': signal_event.workspace_id,
            'correlation_id': signal_event.correlation_id,
            'actor_id': signal_event.actor_id,
            'event_type': 'public.inventory.shelf.created',
            'lifecycle_action': LifecycleAction.CREATED,
        }

    def test_lifecycle_action_comes_from_the_contract(self, signal_event):
        contract = dataclasses.replace(SHELF, lifecycle_action=LifecycleAction.UPDATED)

        envelope = _build(SHELF, 'ProbeSignalEvent')().envelope(signal_event, contract)

        assert envelope['lifecycle_action'] == LifecycleAction.UPDATED

    def test_generate_accepts_a_signal_event(self, signal_event):
        message = _build(SHELF, 'ProbeSignalEvent')().generate(signal_event)

        assert type(message) is InventoryShelfCreatedMessage
        assert message.event_id == signal_event.id_
        assert message.timestamp == signal_event.occurred_on
        assert message.tenant_id == signal_event.tenant_id
        assert message.workspace_id == signal_event.workspace_id
        assert message.correlation_id == signal_event.correlation_id
        assert message.actor_id == signal_event.actor_id

    def test_generating_twice_gives_equal_messages(self, signal_event):
        generator = _build(SHELF, 'ProbeSignalEvent')()

        assert generator.generate(signal_event) == generator.generate(signal_event)

    def test_unknown_signal_event_raises_unknown_event_error(self, signal_event):
        with pytest.raises(UnknownEventError):
            _ShelfGenerator().generate(signal_event)

    def test_event_envelope_is_unchanged(self, shelf_event):
        envelope = _ShelfGenerator().envelope(shelf_event, SHELF)

        assert envelope == {
            'event_id': shelf_event.id_,
            'timestamp': shelf_event.occurred_on,
            'tenant_id': shelf_event.tenant.id_,
            'workspace_id': shelf_event.workspace.id_,
            'correlation_id': shelf_event.correlation_id,
            'actor_id': shelf_event.user.id_,
            'event_type': 'public.inventory.shelf.created',
            'lifecycle_action': LifecycleAction.CREATED,
        }

    def test_event_with_neither_still_raises_value_error(self, make_event):
        event = make_event(NobodyShelfEvent, dict(_SHELF_DATA))

        with pytest.raises(ValueError, match='NobodyShelfEvent'):
            _build(SHELF, 'NobodyShelfEvent')().envelope(event, SHELF)
