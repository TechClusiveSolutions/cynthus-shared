"""Tests for cynthus.messaging.generator.signal_event_reader (SignalEventReader).

The reader is exercised with a local signal, payload, message, generator and ``SignalEvent`` subclasses, so it is tested
apart from the real resource generators. The feature integration test runs the whole round trip: event, generator,
``EventMessagePublisher`` with a recording transport, JSON text, message, reader, equal event.
"""

import dataclasses
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, Field, ValidationError

from cynthus.core.event import EventAction, SignalEvent
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.message import SignalMessage
from cynthus.messaging.common.signal.payload import SignalPayload
from cynthus.messaging.common.signal.public_inventory_base import PublicInventorySignalBase
from cynthus.messaging.component.inventory.message import InventoryShelfCreatedMessage
from cynthus.messaging.generator import SignalEventMismatch, SignalEventReader
from cynthus.messaging.generator.signal_contract import SignalContract
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.publisher.event_message_publisher import EventMessagePublisher
from cynthus.messaging.publisher.signal_publisher import SignalPublisher
from cynthus.messaging.registry import SignalGeneratorRegistry, UnknownEventError
from cynthus.security import TokenClaims


class ProbeSignal(PublicInventorySignalBase):
    """A local signal: public.inventory.probe.created"""

    aggregate = 'probe'
    action = SignalActionType.CREATED


class Kind(str, Enum):
    """An enum field of the payload"""

    SMALL = 'small'
    LARGE = 'large'


ITEM = UUID('12345678-1234-5678-1234-567812345678')
DUE = datetime(2026, 11, 25, 9, 0, tzinfo=timezone.utc)
DUE_TEXT = '2026-11-25T09:00:00Z'


class Detail(BaseModel):
    """A nested value of the payload"""

    label: str
    size: int


class ProbePayload(SignalPayload):
    """The payload of the local signal"""

    schema_version: int = Field(default=1, ge=1)
    probe_id: str
    detail: Detail
    item_id: UUID
    due: datetime
    kind: Kind
    tenant_ref: str
    workspace_ref: str
    service_name: str


class ProbeMessage(SignalMessage[ProbePayload]):
    """The message of the local signal"""

    event_type: str = ProbeSignal.name


class ProbeData(BaseModel):
    """The data model of the local events"""

    probe_id: str = Field(min_length=2)
    detail: Detail
    item_id: UUID
    due: datetime
    kind: Kind


class ProbeEvent(SignalEvent):
    """An event that allows two actions"""

    data_model = ProbeData
    actions = frozenset({EventAction.CREATED, EventAction.UPDATED})


class SoloProbeEvent(SignalEvent):
    """An event that allows one action"""

    data_model = ProbeData
    actions = frozenset({EventAction.CREATED})


class OpenProbeEvent(SignalEvent):
    """An event that declares no allowed actions"""

    data_model = ProbeData


class ResourceProbeEvent(SignalEvent):
    """An event whose contract reads a field from a resource"""


class UserProbeEvent(SignalEvent):
    """An event whose contract reads a field from a user"""


JSON_DATA = {'item_id': str(ITEM), 'due': DUE_TEXT, 'kind': 'large'}

SOURCES = {
    'probe_id': 'data.probe_id',
    'detail': 'data.detail',
    'item_id': 'data.item_id',
    'due': 'data.due',
    'kind': 'data.kind',
    'tenant_ref': 'tenant.id_',
    'workspace_ref': 'workspace.id_',
    'service_name': 'env.SERVICE_NAME',
}


def _contract(event_name='ProbeEvent', **changes):
    contract = SignalContract(
        features=('FT-TEST-001',),
        event=event_name,
        signal=ProbeSignal,
        message=ProbeMessage,
        payload=ProbePayload,
        lifecycle_action=LifecycleAction.CREATED,
        method='created',
        sources=dict(SOURCES),
    )

    return dataclasses.replace(contract, **changes)


class ProbeGenerator(SignalGenerator):
    """Builds the message of a ``ProbeEvent`` from a ``SignalEvent``"""

    contracts = (_contract(),)

    def created(self, event):
        contract = self.contracts[0]
        payload = contract.payload(
            probe_id=event.data['probe_id'],
            detail=event.data['detail'],
            item_id=event.data['item_id'],
            due=event.data['due'],
            kind=event.data['kind'],
            tenant_ref=str(event.tenant_id),
            workspace_ref=str(event.workspace_id),
            service_name='probe-service',
            observed_at=event.occurred_on,
        )
        envelope = {
            'event_id': event.id_,
            'timestamp': event.occurred_on,
            'tenant_id': event.tenant_id,
            'workspace_id': event.workspace_id,
            'correlation_id': event.correlation_id,
            'actor_id': event.actor_id,
            'event_type': contract.signal.name,
            'lifecycle_action': contract.lifecycle_action,
        }

        return contract.message(**envelope, payload=payload)


def _generator(contract):
    class _Generator(SignalGenerator):
        contracts = (contract,)

        def created(self, event):
            raise NotImplementedError

    return _Generator


def _reader(contract=None):
    """A reader over a registry holding only ``contract`` (``ProbeEvent`` when omitted)."""

    return SignalEventReader(SignalGeneratorRegistry([_generator(contract or _contract())]))


def _claims(**changes):
    values = {
        'subject': uuid4(), 'organization_id': uuid4(), 'workspace_id': uuid4(),
        'issued_at': 1_000, 'expires_at': 2_000,
    }

    return TokenClaims(**{**values, **changes})


def _payload(**changes):
    values = {
        'probe_id': 'probe-1', 'detail': Detail(label='blue', size=3), 'item_id': ITEM, 'due': DUE,
        'kind': Kind.LARGE, 'tenant_ref': 't', 'workspace_ref': 'w',
        'service_name': 'svc',
    }

    return ProbePayload(**{**values, **changes})


def _message(claims, **changes):
    """A message carrying the ids of ``claims`` unless ``changes`` say otherwise."""

    values = {
        'event_id': uuid4(),
        'event_type': ProbeSignal.name,
        'lifecycle_action': LifecycleAction.CREATED,
        'correlation_id': uuid4(),
        'tenant_id': claims.tenant_id,
        'workspace_id': claims.workspace_id,
        'actor_id': claims.subject,
        'timestamp': datetime(2026, 11, 25, 10, 30, tzinfo=timezone.utc),
        'payload': _payload(),
    }

    return ProbeMessage(**{**values, **changes})


@pytest.fixture
def claims():
    return _claims()


@pytest.fixture
def message(claims):
    return _message(claims)


class TestExports:
    def test_reader_and_mismatch_are_exported_from_the_package(self):
        import cynthus.messaging.generator as package
        from cynthus.messaging.generator.signal_event_mismatch import SignalEventMismatch as Direct
        from cynthus.messaging.generator.signal_event_reader import SignalEventReader as DirectReader

        assert package.SignalEventReader is DirectReader is SignalEventReader
        assert package.SignalEventMismatch is Direct is SignalEventMismatch


class TestIds:
    def test_ids_come_from_the_claims(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert event.tenant_id == claims.tenant_id
        assert event.workspace_id == claims.workspace_id
        assert event.actor_id == claims.subject

    def test_subject_is_the_actor_and_organization_is_the_tenant(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert event.actor_id == claims.subject
        assert event.tenant_id == claims.organization_id

    def test_ids_equal_the_message_ids(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert event.tenant_id == message.tenant_id
        assert event.workspace_id == message.workspace_id
        assert event.actor_id == message.actor_id

    def test_returns_an_instance_of_the_event_class(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert type(event) is ProbeEvent
        assert isinstance(event, SignalEvent)

    def test_service_id_is_not_set(self, message, claims):
        assert _reader().read(message, claims, ProbeEvent, EventAction.CREATED).service_id is None


class TestEnvelope:
    def test_id_correlation_and_time_come_from_the_message(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert event.id_ == message.event_id
        assert event.correlation_id == message.correlation_id
        assert event.occurred_on == message.timestamp

    def test_ids_are_not_made_up(self, claims):
        first = _reader().read(_message(claims), claims, ProbeEvent, EventAction.CREATED)
        second = _reader().read(_message(claims), claims, ProbeEvent, EventAction.CREATED)

        assert first.id_ != second.id_
        assert first.correlation_id != second.correlation_id

    def test_time_is_the_message_time_not_the_clock(self, claims):
        stamp = datetime(2001, 2, 3, 4, 5, 6, tzinfo=timezone.utc)
        event = _reader().read(_message(claims, timestamp=stamp), claims, ProbeEvent, EventAction.CREATED)

        assert event.occurred_on == stamp
        assert datetime.now(timezone.utc) - event.occurred_on > timedelta(days=1)


class TestData:
    def test_data_holds_the_fields_mapped_to_data_sources(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert event.data == {**JSON_DATA, 'probe_id': 'probe-1', 'detail': {'label': 'blue', 'size': 3}}

    def test_nested_pydantic_value_is_dumped_to_a_dict(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert type(event.data['detail']) is dict
        assert not isinstance(event.data['detail'], BaseModel)

    def test_tenant_workspace_and_env_sources_are_skipped(self, message, claims):
        data = _reader().read(message, claims, ProbeEvent, EventAction.CREATED).data

        assert set(data) == {'probe_id', 'detail', 'item_id', 'due', 'kind'}
        assert 'tenant_ref' not in data
        assert 'workspace_ref' not in data
        assert 'service_name' not in data
        assert 'tenant.id_' not in data

    def test_envelope_payload_fields_are_not_data(self, message, claims):
        data = _reader().read(message, claims, ProbeEvent, EventAction.CREATED).data

        assert 'observed_at' not in data
        assert 'schema_version' not in data
        assert 'metadata' not in data

    def test_data_key_is_the_name_after_the_data_prefix(self, claims):
        sources = {**SOURCES, 'probe_id': 'data.renamed'}
        message = _message(claims)
        event = _reader(_contract('ResourceProbeEvent', sources=sources)).read(
            message, claims, ResourceProbeEvent, EventAction.CREATED
        )

        assert event.data == {**JSON_DATA, 'renamed': 'probe-1', 'detail': {'label': 'blue', 'size': 3}}

    def test_the_message_is_not_changed(self, message, claims):
        before = message.model_dump()

        _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert message.model_dump() == before

    def test_default_registry_reads_a_built_in_shelf_contract(self, claims):
        class InventoryShelfCreatedEvent(SignalEvent):
            actions = frozenset({EventAction.CREATED})

        payload = InventoryShelfCreatedMessage.model_fields['payload'].annotation(
            shelf_id='s-1', location_id='l-1', name='Top', position=4
        )
        message = InventoryShelfCreatedMessage(
            event_type='public.inventory.shelf.created',
            lifecycle_action=LifecycleAction.CREATED,
            correlation_id=uuid4(),
            tenant_id=claims.tenant_id,
            workspace_id=claims.workspace_id,
            actor_id=claims.subject,
            payload=payload,
        )

        event = SignalEventReader().read(message, claims, InventoryShelfCreatedEvent)

        assert event.data == {'shelf_id': 's-1', 'location_id': 'l-1', 'name': 'Top', 'position': 4}
        assert event.action == EventAction.CREATED


class TestJsonData:
    def test_uuid_datetime_and_enum_become_text(self, message, claims):
        data = _reader().read(message, claims, ProbeEvent, EventAction.CREATED).data

        assert data['item_id'] == str(ITEM)
        assert data['due'] == DUE_TEXT
        assert data['kind'] == 'large'
        assert type(data['kind']) is str
        assert type(data['item_id']) is str
        assert type(data['due']) is str

    def test_data_model_parses_the_typed_values_back(self, message, claims):
        parsed = _reader().read(message, claims, ProbeEvent, EventAction.CREATED).parsed_data(ProbeData)

        assert parsed.item_id == ITEM
        assert parsed.due == DUE
        assert parsed.kind is Kind.LARGE


class TestPayloadClass:
    def test_another_payload_class_raises_mismatch_naming_payload(self, claims):
        message = SignalMessage(
            event_id=uuid4(), event_type=ProbeSignal.name, lifecycle_action=LifecycleAction.CREATED,
            correlation_id=uuid4(), tenant_id=claims.tenant_id, workspace_id=claims.workspace_id,
            actor_id=claims.subject, payload=SignalPayload(schema_version=1),
        )

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        text = str(raised.value)

        assert type(raised.value) is SignalEventMismatch
        assert 'payload' in text
        for value in (claims.tenant_id, claims.workspace_id, claims.subject, message.event_id, message.correlation_id):
            assert str(value) not in text


class TestMismatch:
    @pytest.mark.parametrize('field', ['tenant_id', 'workspace_id'])
    def test_different_tenant_or_workspace_in_the_claims(self, claims, field):
        message = _message(claims, **{field: uuid4()})

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert type(raised.value) is SignalEventMismatch
        assert field in str(raised.value)

    def test_different_actor_in_the_claims(self, claims):
        message = _message(claims, actor_id=uuid4())

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert 'actor_id' in str(raised.value)

    @pytest.mark.parametrize('field', ['tenant_id', 'workspace_id', 'actor_id'])
    def test_the_text_names_only_the_field_that_differs(self, claims, field):
        message = _message(claims, **{field: uuid4()})
        others = {'tenant_id', 'workspace_id', 'actor_id'} - {field}

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert field in str(raised.value)
        assert not any(other in str(raised.value) for other in others)

    @pytest.mark.parametrize('field', ['tenant_id', 'workspace_id', 'actor_id'])
    def test_the_text_contains_no_id_value(self, claims, field):
        foreign = uuid4()
        message = _message(claims, **{field: foreign})

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        text = str(raised.value)
        ids = [foreign, claims.tenant_id, claims.workspace_id, claims.subject, message.event_id, message.correlation_id]

        for value in ids:
            assert str(value) not in text
            assert value.hex not in text
            assert str(value)[:8] not in text

    def test_it_is_a_value_error(self, claims):
        with pytest.raises(ValueError):
            _reader().read(_message(claims, tenant_id=uuid4()), claims, ProbeEvent, EventAction.CREATED)

    def test_tenant_is_named_first_when_all_three_differ(self, claims):
        message = _message(claims, tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4())

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert 'tenant_id' in str(raised.value)

    def test_tenant_is_named_before_the_actor(self, claims):
        message = _message(claims, tenant_id=uuid4(), actor_id=uuid4())

        with pytest.raises(SignalEventMismatch, match='tenant_id'):
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

    def test_workspace_is_named_before_the_actor(self, claims):
        message = _message(claims, workspace_id=uuid4(), actor_id=uuid4())

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert 'workspace_id' in str(raised.value)
        assert 'actor_id' not in str(raised.value)

    def test_tenant_is_named_before_the_workspace(self, claims):
        message = _message(claims, tenant_id=uuid4(), workspace_id=uuid4())

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert 'tenant_id' in str(raised.value)
        assert 'workspace_id' not in str(raised.value)

    def test_the_claims_are_checked_not_the_other_way(self, message):
        other = _claims()

        with pytest.raises(SignalEventMismatch, match='tenant_id'):
            _reader().read(message, other, ProbeEvent, EventAction.CREATED)


class TestOtherSignalAndUnknownEvent:
    def test_message_of_another_signal(self, claims):
        message = _message(claims, event_type='public.inventory.other.created')

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert type(raised.value) is SignalEventMismatch
        assert 'event_type' in str(raised.value)

    def test_event_type_is_named_before_any_id(self, claims):
        message = _message(
            claims, event_type='public.inventory.other.created', tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4()
        )

        with pytest.raises(SignalEventMismatch) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert 'event_type' in str(raised.value)
        assert 'tenant_id' not in str(raised.value)

    def test_event_class_with_no_contract(self, message, claims):
        with pytest.raises(UnknownEventError, match='SoloProbeEvent'):
            _reader().read(message, claims, SoloProbeEvent, EventAction.CREATED)

    def test_the_default_registry_has_no_contract_for_a_local_event(self, message, claims):
        with pytest.raises(UnknownEventError):
            SignalEventReader().read(message, claims, ProbeEvent, EventAction.CREATED)

    def test_an_empty_registry_is_honoured_not_replaced_by_the_default(self, message, claims):
        class InventoryShelfCreatedEvent(SignalEvent):
            pass

        with pytest.raises(UnknownEventError):
            SignalEventReader(SignalGeneratorRegistry([])).read(message, claims, InventoryShelfCreatedEvent)

    def test_unknown_event_is_reported_before_a_mismatch(self, claims):
        message = _message(claims, event_type='public.inventory.other.created', tenant_id=uuid4())

        with pytest.raises(UnknownEventError):
            _reader().read(message, claims, SoloProbeEvent, EventAction.CREATED)

    def test_subclass_of_a_registered_event_is_not_matched(self, message, claims):
        class ChildProbeEvent(ProbeEvent):
            pass

        with pytest.raises(UnknownEventError, match='ChildProbeEvent'):
            _reader().read(message, claims, ChildProbeEvent, EventAction.CREATED)


class TestSourcesThatCannotBeRead:
    @pytest.mark.parametrize(
        'source, event_name', [('resource.id_', 'ResourceProbeEvent'), ('user.id_', 'UserProbeEvent')]
    )
    def test_resource_or_user_source_raises_value_error_naming_the_field(self, message, claims, source, event_name):
        event_class = {'ResourceProbeEvent': ResourceProbeEvent, 'UserProbeEvent': UserProbeEvent}[event_name]
        contract = _contract(event_name, sources={**SOURCES, 'tenant_ref': source})

        with pytest.raises(ValueError) as raised:
            _reader(contract).read(message, claims, event_class, EventAction.CREATED)

        assert type(raised.value) is ValueError
        assert 'tenant_ref' in str(raised.value)

    def test_the_error_is_not_a_mismatch_or_a_validation_error(self, message, claims):
        contract = _contract('ResourceProbeEvent', sources={**SOURCES, 'workspace_ref': 'resource.id_'})

        with pytest.raises(ValueError) as raised:
            _reader(contract).read(message, claims, ResourceProbeEvent, EventAction.CREATED)

        assert not isinstance(raised.value, (SignalEventMismatch, ValidationError))
        assert 'workspace_ref' in str(raised.value)


class TestAction:
    def test_explicit_action_is_used(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.UPDATED)

        assert event.action == EventAction.UPDATED

    def test_explicit_action_can_be_passed_by_keyword(self, message, claims):
        assert _reader().read(message, claims, ProbeEvent, action=EventAction.CREATED).action == EventAction.CREATED

    def test_the_single_allowed_action_is_the_default(self, message, claims):
        event = _reader(_contract('SoloProbeEvent')).read(message, claims, SoloProbeEvent)

        assert event.action == EventAction.CREATED

    def test_explicit_action_wins_over_the_single_allowed_action(self, message, claims):
        with pytest.raises(ValidationError):
            _reader(_contract('SoloProbeEvent')).read(message, claims, SoloProbeEvent, EventAction.DELETED)

    def test_the_lifecycle_action_of_the_message_is_not_used(self, claims):
        message = _message(claims, lifecycle_action=LifecycleAction.UPDATED)

        with pytest.raises(ValueError, match='action is required') as raised:
            _reader().read(message, claims, ProbeEvent)

        assert type(raised.value) is ValueError

    def test_missing_action_with_several_allowed_actions(self, message, claims):
        with pytest.raises(ValueError, match='action is required') as raised:
            _reader().read(message, claims, ProbeEvent)

        assert type(raised.value) is ValueError

    def test_missing_action_with_no_declared_actions(self, message, claims):
        with pytest.raises(ValueError, match='action is required') as raised:
            _reader(_contract('OpenProbeEvent')).read(message, claims, OpenProbeEvent)

        assert type(raised.value) is ValueError

    def test_explicit_action_with_no_declared_actions_is_accepted(self, message, claims):
        event = _reader(_contract('OpenProbeEvent')).read(message, claims, OpenProbeEvent, EventAction.DELETED)

        assert event.action == EventAction.DELETED

    def test_action_the_class_does_not_allow_raises_validation_error(self, message, claims):
        with pytest.raises(ValidationError):
            _reader().read(message, claims, ProbeEvent, EventAction.DELETED)

    def test_validation_error_is_not_wrapped(self, message, claims):
        with pytest.raises(ValidationError) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.DELETED)

        assert type(raised.value) is ValidationError
        assert 'deleted' in str(raised.value)


class TestDataModel:
    def test_data_the_model_rejects_raises_validation_error(self, claims):
        message = _message(claims, payload=_payload(probe_id='x'))

        with pytest.raises(ValidationError) as raised:
            _reader().read(message, claims, ProbeEvent, EventAction.CREATED)

        assert type(raised.value) is ValidationError
        assert 'probe_id' in str(raised.value)

    def test_accepted_data_can_be_parsed_again(self, message, claims):
        event = _reader().read(message, claims, ProbeEvent, EventAction.CREATED)
        parsed = event.parsed_data(ProbeData)

        assert parsed.probe_id == 'probe-1'
        assert parsed.detail == Detail(label='blue', size=3)


class _Recording(SignalPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, message, access_token=None, *, topic=None):
        self.calls.append((message, access_token, topic))


class TestRoundTrip:
    @pytest.mark.asyncio
    async def test_event_to_message_to_json_to_event(self):
        claims = _claims()
        event = ProbeEvent(
            tenant_id=claims.tenant_id,
            workspace_id=claims.workspace_id,
            actor_id=claims.subject,
            action=EventAction.CREATED,
            data={**JSON_DATA, 'probe_id': 'probe-7', 'detail': {'label': 'green', 'size': 9}},
        )
        transport = _Recording()
        registry = SignalGeneratorRegistry([ProbeGenerator])

        published = await EventMessagePublisher(transport, registry).publish(event, 'token')
        text = transport.calls[0][0].model_dump_json()
        received = ProbeMessage.model_validate_json(text)
        read = SignalEventReader(registry).read(received, claims, ProbeEvent, EventAction.CREATED)

        assert len(transport.calls) == 1
        assert published is transport.calls[0][0]
        assert read.id_ == event.id_
        assert read.tenant_id == event.tenant_id
        assert read.workspace_id == event.workspace_id
        assert read.actor_id == event.actor_id
        assert read.correlation_id == event.correlation_id
        assert read.occurred_on == event.occurred_on
        assert read.action == event.action
        assert read.data == event.data
        assert read == event

    @pytest.mark.asyncio
    async def test_a_message_for_another_user_is_refused_after_the_round_trip(self):
        claims = _claims()
        event = ProbeEvent(
            tenant_id=claims.tenant_id, workspace_id=claims.workspace_id, actor_id=claims.subject,
            action=EventAction.UPDATED, data={**JSON_DATA, 'probe_id': 'probe-7', 'detail': {'label': 'green', 'size': 9}},
        )
        transport = _Recording()
        registry = SignalGeneratorRegistry([ProbeGenerator])

        await EventMessagePublisher(transport, registry).publish(event)
        received = ProbeMessage.model_validate_json(transport.calls[0][0].model_dump_json())

        with pytest.raises(SignalEventMismatch, match='actor_id'):
            SignalEventReader(registry).read(received, _claims(
                organization_id=claims.tenant_id, workspace_id=claims.workspace_id
            ), ProbeEvent, EventAction.UPDATED)
