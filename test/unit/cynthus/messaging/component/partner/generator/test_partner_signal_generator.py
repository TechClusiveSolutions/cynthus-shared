"""Tests for cynthus.messaging.component.partner.generator.partner_signal_generator (PartnerSignalGenerator)."""

from uuid import uuid4

import pytest

from cynthus.core.event import (
    EventAction,
    InventoryEvent,
    PartnerServiceListRequestedEvent,
    PartnerServiceListRespondedEvent,
)
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.public_partner_service_list_requested import (
    PublicPartnerServiceListRequestedSignal,
)
from cynthus.messaging.common.signal.public_partner_service_list_responded import (
    PublicPartnerServiceListRespondedSignal,
)
from cynthus.messaging.component.partner.generator import PartnerSignalGenerator
from cynthus.messaging.component.partner.generator.partner_signal_generator import PartnerSignalGenerator as Direct
from cynthus.messaging.component.partner.message import (
    PartnerServiceListRequestedMessage,
    PartnerServiceListRespondedMessage,
)
from cynthus.messaging.component.partner.payload import (
    PartnerServiceListRequestedPayload,
    PartnerServiceListRespondedPayload,
)
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.registry import SignalGeneratorRegistry, UnknownEventError

REQUESTED, RESPONDED = PartnerSignalGenerator.contracts


def _ids():
    return {'tenant_id': uuid4(), 'workspace_id': uuid4(), 'actor_id': uuid4()}


def _requested(data=None, **ids):
    return PartnerServiceListRequestedEvent(
        **(ids or _ids()), action=EventAction.RETRIEVED, data={} if data is None else data,
    )


def _responded(data, **ids):
    return PartnerServiceListRespondedEvent(**(ids or _ids()), action=EventAction.RETRIEVED, data=data)


def test_is_exported_from_the_package():
    assert Direct is PartnerSignalGenerator


def test_is_a_signal_generator():
    assert issubclass(PartnerSignalGenerator, SignalGenerator)


class TestContracts:
    def test_two_contracts_in_order(self):
        assert len(PartnerSignalGenerator.contracts) == 2

    def test_requested_contract(self):
        assert REQUESTED.features == ('FT-SR-006',)
        assert REQUESTED.event == 'PartnerServiceListRequestedEvent'
        assert REQUESTED.signal is PublicPartnerServiceListRequestedSignal
        assert REQUESTED.message is PartnerServiceListRequestedMessage
        assert REQUESTED.payload is PartnerServiceListRequestedPayload
        assert REQUESTED.lifecycle_action == LifecycleAction.UPDATED
        assert REQUESTED.method == 'requested'
        assert REQUESTED.sources == {'schema_version': 'data.schema_version', 'filters': 'data.filters'}

    def test_responded_contract(self):
        assert RESPONDED.features == ('FT-SR-006',)
        assert RESPONDED.event == 'PartnerServiceListRespondedEvent'
        assert RESPONDED.signal is PublicPartnerServiceListRespondedSignal
        assert RESPONDED.message is PartnerServiceListRespondedMessage
        assert RESPONDED.payload is PartnerServiceListRespondedPayload
        assert RESPONDED.lifecycle_action == LifecycleAction.UPDATED
        assert RESPONDED.method == 'responded'
        assert RESPONDED.sources == {
            'schema_version': 'data.schema_version', 'status': 'data.status', 'result': 'data.result',
            'error': 'data.error',
        }

    def test_methods_exist(self):
        assert callable(PartnerSignalGenerator().requested)
        assert callable(PartnerSignalGenerator().responded)


class TestRequested:
    def test_message_type_and_envelope(self):
        event = _requested({'filters': {'name': 'Butcher'}})

        message = PartnerSignalGenerator().generate(event)

        assert type(message) is PartnerServiceListRequestedMessage
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on
        assert message.tenant_id == event.tenant_id
        assert message.workspace_id == event.workspace_id
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.actor_id
        assert message.event_type == PublicPartnerServiceListRequestedSignal.name
        assert message.lifecycle_action == LifecycleAction.UPDATED

    def test_payload_equals_the_data(self):
        message = PartnerSignalGenerator().generate(_requested({'filters': {'name': 'Butcher'}}))

        assert message.payload.schema_version == 1
        assert message.payload.filters.name == 'Butcher'

    def test_observed_at_is_the_occurred_on(self):
        event = _requested()

        assert PartnerSignalGenerator().generate(event).payload.observed_at == event.occurred_on

    def test_no_data_gives_the_defaults(self):
        message = PartnerSignalGenerator().generate(_requested())

        assert message.payload.schema_version == 1
        assert message.payload.filters.name is None

    def test_schema_version_comes_from_the_data(self):
        assert PartnerSignalGenerator().generate(_requested({'schema_version': 3})).payload.schema_version == 3

    def test_called_directly(self):
        event = _requested({'filters': {'name': 'x'}})
        generator = PartnerSignalGenerator()

        assert generator.requested(event) == generator.generate(event)


class TestResponded:
    def test_message_type_and_envelope(self):
        event = _responded({'status': 200})

        message = PartnerSignalGenerator().generate(event)

        assert type(message) is PartnerServiceListRespondedMessage
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on
        assert message.tenant_id == event.tenant_id
        assert message.workspace_id == event.workspace_id
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.actor_id
        assert message.event_type == PublicPartnerServiceListRespondedSignal.name
        assert message.lifecycle_action == LifecycleAction.UPDATED

    def test_payload_equals_the_data(self):
        first, second = uuid4(), uuid4()
        event = _responded({
            'status': 200, 'result': [{'id': str(first), 'name': 'A'}, {'id': str(second), 'name': 'B'}],
        })

        payload = PartnerSignalGenerator().generate(event).payload

        assert payload.status == 200
        assert payload.error is None
        assert [(item.id, item.name) for item in payload.result] == [(first, 'A'), (second, 'B')]
        assert payload.observed_at == event.occurred_on

    def test_error_payload(self):
        payload = PartnerSignalGenerator().generate(_responded({'status': 422, 'error': 'bad filter'})).payload

        assert payload.status == 422
        assert payload.error == 'bad filter'
        assert payload.result is None

    def test_answering_event_generates(self):
        request = _requested({'filters': {'name': 'x'}})
        response = PartnerServiceListRespondedEvent.answering(request, status=200, items=[(uuid4(), 'A')])

        message = PartnerSignalGenerator().generate(response)

        assert message.correlation_id == request.correlation_id
        assert message.payload.result[0].name == 'A'


class TestPurity:
    def test_equal_event_gives_equal_message(self):
        event = _requested({'filters': {'name': 'x'}})
        generator = PartnerSignalGenerator()

        assert generator.generate(event) == generator.generate(event)
        assert generator.generate(event) == PartnerSignalGenerator().generate(event)

    def test_equal_responded_event_gives_equal_message(self):
        event = _responded({'status': 200, 'result': [{'id': str(uuid4()), 'name': 'A'}]})

        assert PartnerSignalGenerator().generate(event) == PartnerSignalGenerator().generate(event)

    def test_event_is_unchanged(self):
        event = _responded({'status': 200, 'result': [{'id': str(uuid4()), 'name': 'A'}]})
        before = event.model_dump()

        PartnerSignalGenerator().generate(event)

        assert event.model_dump() == before

    def test_repeated_calls_leave_the_event_unchanged_and_the_message_equal(self):
        event = _requested({'filters': {'name': 'x'}})
        before = event.model_dump()
        generator = PartnerSignalGenerator()

        first, second = generator.generate(event), generator.generate(event)

        assert first == second
        assert first is not second
        assert event.model_dump() == before


class TestRegistry:
    def test_default_registry_holds_both_events(self):
        registry = SignalGeneratorRegistry.default()

        assert registry.contract_for('PartnerServiceListRequestedEvent') is REQUESTED
        assert registry.contract_for('PartnerServiceListRespondedEvent') is RESPONDED
        assert registry.signal_for('PartnerServiceListRequestedEvent') is PublicPartnerServiceListRequestedSignal
        assert registry.signal_for('PartnerServiceListRespondedEvent') is PublicPartnerServiceListRespondedSignal

    def test_generator_for_a_signal_event(self):
        found = SignalGeneratorRegistry.default().generator_for(_requested())

        assert (found if isinstance(found, type) else type(found)) is PartnerSignalGenerator

    def test_event_class_with_no_generator_raises_unknown_event_error(self, make_event):
        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry.default().generator_for(make_event(InventoryEvent, {}))

    def test_signal_event_with_no_generator_raises_unknown_event_error(self):
        from cynthus.core.event import PartnerEvent

        event = PartnerEvent(**_ids(), action=EventAction.RETRIEVED, data={})

        with pytest.raises(UnknownEventError):
            SignalGeneratorRegistry.default().generator_for(event)
