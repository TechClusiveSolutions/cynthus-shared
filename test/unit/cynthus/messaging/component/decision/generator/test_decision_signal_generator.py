"""Tests for cynthus.messaging.component.decision.generator.decision_signal_generator (DecisionSignalGenerator)."""

import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from cynthus.core.event import (
    DecisionCondition,
    EventAction,
    EventRequest,
    EventRequestDecision,
    EventRequestDecisionAnswer,
    EventRequestDecisionEvent,
    PartnerServiceListRequestedEvent,
)
from cynthus.core.test.factory import UserFactory
from cynthus.messaging.common.signal import (
    PublicDecisionEventRequestApprovedConditionallySignal,
    PublicDecisionEventRequestApprovedSignal,
    PublicDecisionEventRequestDeniedConditionallySignal,
    PublicDecisionEventRequestDeniedSignal,
    SignalPayload,
)
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.component.decision.generator import DecisionSignalGenerator
from cynthus.messaging.component.decision.generator.decision_signal_generator import DecisionSignalGenerator as Direct
from cynthus.messaging.component.decision.payload import EventRequestDecisionPayload
from cynthus.messaging.generator.signal_generator import SignalGenerator
from cynthus.messaging.registry import SignalGeneratorRegistry, UnknownEventError

CASES = [
    (EventRequestDecisionAnswer.APPROVED, 'DecisionEventRequestApprovedEvent', PublicDecisionEventRequestApprovedSignal),
    (EventRequestDecisionAnswer.APPROVED_CONDITIONALLY, 'DecisionEventRequestApprovedConditionallyEvent',
     PublicDecisionEventRequestApprovedConditionallySignal),
    (EventRequestDecisionAnswer.DENIED, 'DecisionEventRequestDeniedEvent', PublicDecisionEventRequestDeniedSignal),
    (EventRequestDecisionAnswer.DENIED_CONDITIONALLY, 'DecisionEventRequestDeniedConditionallyEvent',
     PublicDecisionEventRequestDeniedConditionallySignal),
]
NOW = datetime(2026, 11, 27, 9, 0, tzinfo=timezone.utc)
PAYLOAD_FIELDS = set(EventRequestDecisionPayload.model_fields) - (set(SignalPayload.model_fields) - {'schema_version'})


def _event(answer=EventRequestDecisionAnswer.APPROVED_CONDITIONALLY, conditions=None, in_reply_to=None,
           determined_by=...):
    requestor = UserFactory()
    request = EventRequest.model_construct(
        event=PartnerServiceListRequestedEvent(
            tenant_id=uuid4(), workspace_id=uuid4(), actor_id=requestor.id_, action=EventAction.RETRIEVED, data={},
        ),
        requestor=requestor, in_reply_to=in_reply_to,
    )
    decision = EventRequestDecision(
        answer=answer, answer_reason='approval_required', determined_by=uuid4() if determined_by is ... else determined_by, determined_on=NOW,
        conditions=[
            DecisionCondition(condition='approval_granted', expires_at=NOW + timedelta(days=5)),
            DecisionCondition(condition='second'),
        ] if conditions is None else conditions,
    )

    return EventRequestDecisionEvent.deciding(request, decision), request, decision


def test_is_exported_from_the_package():
    assert Direct is DecisionSignalGenerator


def test_is_a_signal_generator():
    assert issubclass(DecisionSignalGenerator, SignalGenerator)


class TestContracts:
    def test_four_contracts(self):
        assert [c.event for c in DecisionSignalGenerator.contracts].__len__() == 4
        assert {c.event for c in DecisionSignalGenerator.contracts} == {name for _, name, _ in CASES}

    @pytest.mark.parametrize('answer, event_name, signal', CASES)
    def test_contract(self, answer, event_name, signal):
        contract = next(c for c in DecisionSignalGenerator.contracts if c.event == event_name)

        assert contract.signal is signal
        assert contract.payload is EventRequestDecisionPayload
        assert contract.lifecycle_action == LifecycleAction.CREATED
        assert contract.message.model_fields['event_type'].default == signal.name
        assert contract.features and all(re.fullmatch(r'FT-[A-Z]{2}-\d{3}', f) for f in contract.features)
        assert callable(getattr(DecisionSignalGenerator(), contract.method))

    @pytest.mark.parametrize('answer, event_name, signal', CASES)
    def test_every_payload_field_maps_to_the_same_data_field(self, answer, event_name, signal):
        contract = next(c for c in DecisionSignalGenerator.contracts if c.event == event_name)

        assert contract.sources == {name: f'data.{name}' for name in PAYLOAD_FIELDS}

    def test_methods_and_signals_are_distinct(self):
        contracts = DecisionSignalGenerator.contracts

        assert len({c.method for c in contracts}) == 4
        assert len({c.signal.name for c in contracts}) == 4


@pytest.mark.parametrize('answer, event_name, signal', CASES)
class TestGenerate:
    def test_message_type_and_envelope(self, answer, event_name, signal):
        event, _, _ = _event(answer)

        message = DecisionSignalGenerator().generate(event)

        assert type(event).__name__ == event_name
        assert message.event_type == signal.name
        assert message.event_id == event.id_
        assert message.timestamp == event.occurred_on
        assert message.tenant_id == event.tenant_id
        assert message.workspace_id == event.workspace_id
        assert message.correlation_id == event.correlation_id
        assert message.actor_id == event.actor_id
        assert message.lifecycle_action == LifecycleAction.CREATED
        assert isinstance(message.payload, EventRequestDecisionPayload)

    def test_payload_fields_equal_the_decision(self, answer, event_name, signal):
        in_reply_to = uuid4()
        event, request, decision = _event(answer, in_reply_to=in_reply_to)

        payload = DecisionSignalGenerator().generate(event).payload

        assert payload.schema_version == 1
        assert payload.event_request_id == request.id_
        assert payload.in_reply_to == in_reply_to
        assert payload.requested_event_type == 'partner_service_list_requested'
        assert payload.requested_action == 'retrieved'
        assert payload.requestor_id == request.requestor.id_
        assert payload.answer == decision.answer.value
        assert payload.answer_reason == decision.answer_reason
        assert payload.determined_by == decision.determined_by
        assert payload.determined_on == decision.determined_on
        assert payload.observed_at == event.occurred_on

    def test_conditions_are_included(self, answer, event_name, signal):
        event, _, decision = _event(answer)

        payload = DecisionSignalGenerator().generate(event).payload

        assert [(c.condition, c.status, c.expires_at) for c in payload.conditions] == [
            (c.condition, c.status.value, c.expires_at) for c in decision.conditions
        ]
        assert len(payload.conditions) == 2

    def test_no_conditions_give_an_empty_list(self, answer, event_name, signal):
        event, _, _ = _event(answer, conditions=[])

        assert DecisionSignalGenerator().generate(event).payload.conditions == []

    def test_no_reply_and_no_determining_service_give_none(self, answer, event_name, signal):
        payload = DecisionSignalGenerator().generate(_event(answer, determined_by=None)[0]).payload

        assert payload.in_reply_to is None
        assert payload.determined_by is None

    def test_equal_event_gives_equal_message(self, answer, event_name, signal):
        event, _, _ = _event(answer)

        assert DecisionSignalGenerator().generate(event) == DecisionSignalGenerator().generate(event.model_copy())

    def test_event_is_unchanged(self, answer, event_name, signal):
        event, _, _ = _event(answer)
        before = event.model_dump()

        DecisionSignalGenerator().generate(event)

        assert event.model_dump() == before

    def test_generated_through_the_method_of_the_contract(self, answer, event_name, signal):
        event, _, _ = _event(answer)
        contract = next(c for c in DecisionSignalGenerator.contracts if c.event == event_name)
        generator = DecisionSignalGenerator()

        assert getattr(generator, contract.method)(event) == generator.generate(event)


class TestFailures:
    def test_an_event_class_with_no_contract_raises_unknown_event_error(self):
        event = PartnerServiceListRequestedEvent(
            tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=EventAction.RETRIEVED, data={},
        )

        with pytest.raises(UnknownEventError):
            DecisionSignalGenerator().generate(event)

    def test_the_base_decision_event_has_no_contract(self):
        event, _, _ = _event()
        base = EventRequestDecisionEvent.model_construct(**event.model_dump())

        with pytest.raises(UnknownEventError):
            DecisionSignalGenerator().generate(base)


class TestRegistry:
    @pytest.mark.parametrize('answer, event_name, signal', CASES)
    def test_default_registry_holds_the_event(self, answer, event_name, signal):
        registry = SignalGeneratorRegistry.default()

        assert registry.signal_for(event_name) is signal
        assert registry.event_name_for(signal) == event_name

    @pytest.mark.parametrize('answer, event_name, signal', CASES)
    def test_generator_for_the_event(self, answer, event_name, signal):
        found = SignalGeneratorRegistry.default().generator_for(_event(answer)[0])

        assert (found if isinstance(found, type) else type(found)) is DecisionSignalGenerator

    def test_default_registry_holds_the_four_contracts(self):
        contracts = set(SignalGeneratorRegistry.default().contracts())

        assert set(DecisionSignalGenerator.contracts) <= contracts
