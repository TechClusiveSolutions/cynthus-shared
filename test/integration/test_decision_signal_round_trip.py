"""Feature integration (AC11d): decisions built by hand go through ``EventRequestDecisionEvent.deciding``,
``EventMessagePublisher`` with a recording transport, JSON text and ``SignalEventReader.read``."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.core.event import (
    DecisionCondition,
    DecisionEventRequestApprovedConditionallyEvent,
    DecisionEventRequestApprovedEvent,
    DecisionEventRequestDeniedConditionallyEvent,
    DecisionEventRequestDeniedEvent,
    EventAction,
    EventRequest,
    EventRequestDecisionData,
    EventRequestDecisionEvent,
    EventRequestResponse,
    PartnerServiceListRequestedEvent,
)
from cynthus.core.test.factory import UserFactory
from cynthus.messaging.common.signal import (
    PublicDecisionEventRequestApprovedConditionallySignal,
    PublicDecisionEventRequestApprovedSignal,
    PublicDecisionEventRequestDeniedConditionallySignal,
    PublicDecisionEventRequestDeniedSignal,
)
from cynthus.messaging.generator import SignalEventReader
from cynthus.messaging.generator.signal_event_mismatch import SignalEventMismatch
from cynthus.messaging.publisher.event_message_publisher import EventMessagePublisher
from cynthus.messaging.publisher.signal_publisher import SignalPublisher
from cynthus.messaging.registry import UnknownEventError
from cynthus.security import TokenClaims

NOW = datetime(2026, 11, 27, 9, 0, tzinfo=timezone.utc)


class _Recording(SignalPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, message, access_token=None, *, topic=None):
        self.calls.append((message, access_token, topic))


def _response():
    requestor = UserFactory()
    request = EventRequest.model_construct(
        event=PartnerServiceListRequestedEvent(
            tenant_id=uuid4(), workspace_id=uuid4(), actor_id=requestor.id_, action=EventAction.RETRIEVED, data={},
        ),
        requestor=requestor,
    )

    return EventRequestResponse(request=request)


def _claims(event):
    return TokenClaims(
        subject=event.actor_id, organization_id=event.tenant_id, workspace_id=event.workspace_id,
        issued_at=1_000, expires_at=2_000,
    )


def _decided(response, decision):
    return EventRequestDecisionEvent.deciding(response.request, decision)


def _approved():
    response = _response()

    return response, _decided(response, response.approve('approval_granted', determined_by=uuid4()))


def _conditional():
    response = _response()
    condition = DecisionCondition(condition='approval_granted', expires_at=NOW + timedelta(days=5))

    return response, _decided(response, response.conditionally_approve('approval_required', [condition]))


def _denied():
    response = _response()

    return response, _decided(response, response.deny('approval_denied'))


def _denied_conditionally():
    response = _response()

    return response, _decided(response, response.conditionally_deny('approval_required', ['approval_granted']))


CASES = [
    (_approved, DecisionEventRequestApprovedEvent, PublicDecisionEventRequestApprovedSignal),
    (_conditional, DecisionEventRequestApprovedConditionallyEvent, PublicDecisionEventRequestApprovedConditionallySignal),
    (_denied, DecisionEventRequestDeniedEvent, PublicDecisionEventRequestDeniedSignal),
    (_denied_conditionally, DecisionEventRequestDeniedConditionallyEvent, PublicDecisionEventRequestDeniedConditionallySignal),
]


async def _publish(event):
    transport = _Recording()

    await EventMessagePublisher(transport).publish(event, 'token')

    assert len(transport.calls) == 1

    return transport.calls[0][0]


@pytest.mark.asyncio
class TestDecisionRoundTrip:
    @pytest.mark.parametrize('build, event_class, signal', CASES)
    async def test_a_decision_is_published_as_its_signal(self, build, event_class, signal):
        response, event = build()

        message = await _publish(event)

        assert type(event) is event_class
        assert message.event_type == signal.name
        assert message.correlation_id == response.request.event.correlation_id
        assert message.tenant_id == response.request.event.tenant_id
        assert message.actor_id == response.request.requestor.id_
        decision = response.decision
        assert message.payload.event_request_id == response.request.id_
        assert message.payload.answer == decision.answer.value
        assert message.payload.answer_reason == decision.answer_reason
        assert message.payload.requested_event_type == 'partner_service_list_requested'
        assert [c.condition for c in message.payload.conditions] == [c.condition for c in decision.conditions]

    async def test_four_decisions_give_four_distinct_signals(self):
        names = set()
        answers = set()

        for build, _, _ in CASES:
            message = await _publish(build()[1])
            names.add(message.event_type)
            answers.add(message.payload.answer)

        assert names == {signal.name for _, _, signal in CASES}
        assert answers == {'approved', 'approved_conditionally', 'denied', 'denied_conditionally'}

    @pytest.mark.parametrize('build, event_class, signal', CASES)
    async def test_the_signal_reads_back_as_an_equal_event(self, build, event_class, signal):
        response, event = build()
        message = await _publish(event)

        received = type(message).model_validate_json(message.model_dump_json())
        read = SignalEventReader().read(received, _claims(event), event_class)

        assert type(read) is event_class
        assert read.id_ == event.id_
        assert read.correlation_id == event.correlation_id
        assert read.occurred_on == event.occurred_on
        assert read.tenant_id == event.tenant_id
        assert read.workspace_id == event.workspace_id
        assert read.actor_id == event.actor_id
        assert read.action == EventAction.CREATED
        assert read.parsed_data(EventRequestDecisionData) == event.parsed_data(EventRequestDecisionData)

    async def test_conditions_survive_the_trip(self):
        response, event = _conditional()
        message = await _publish(event)

        read = SignalEventReader().read(
            type(message).model_validate_json(message.model_dump_json()), _claims(event),
            DecisionEventRequestApprovedConditionallyEvent,
        )

        conditions = read.parsed_data(EventRequestDecisionData).conditions
        assert [(c.condition, c.status, c.expires_at) for c in conditions] == [
            ('approval_granted', 'open', NOW + timedelta(days=5)),
        ]

    async def test_reading_with_the_wrong_event_class_is_a_mismatch(self):
        _, event = _approved()
        message = await _publish(event)

        with pytest.raises(SignalEventMismatch):
            SignalEventReader().read(message, _claims(event), DecisionEventRequestDeniedEvent)

    async def test_reading_with_other_claims_is_a_mismatch(self):
        _, event = _approved()
        message = await _publish(event)
        other = TokenClaims(
            subject=uuid4(), organization_id=event.tenant_id, workspace_id=event.workspace_id,
            issued_at=1_000, expires_at=2_000,
        )

        with pytest.raises(SignalEventMismatch):
            SignalEventReader().read(message, other, DecisionEventRequestApprovedEvent)

    async def test_reading_the_base_class_is_an_unknown_event(self):
        _, event = _approved()
        message = await _publish(event)

        with pytest.raises(UnknownEventError):
            SignalEventReader().read(message, _claims(event), EventRequestDecisionEvent)


@pytest.mark.asyncio
class TestAnswerMustMatchTheSignal:
    @pytest.mark.parametrize('build, event_class, signal', CASES)
    async def test_a_payload_answer_that_differs_from_the_event_class_is_refused(self, build, event_class, signal):
        _, event = build()
        message = await _publish(event)
        answer = 'denied' if message.payload.answer != 'denied' else 'approved'
        forged = message.model_copy(update={'payload': message.payload.model_copy(update={'answer': answer})})
        received = type(message).model_validate_json(forged.model_dump_json())

        with pytest.raises(ValidationError):
            SignalEventReader().read(received, _claims(event), event_class)
