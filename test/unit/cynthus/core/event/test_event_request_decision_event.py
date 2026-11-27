"""Tests for cynthus.core.event.event_request_decision_event (EventRequestDecisionEvent and ``deciding``)."""

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
    EventRequestDecision,
    EventRequestDecisionAnswer,
    EventRequestDecisionData,
    PartnerServiceListRequestedEvent,
    SignalEvent,
)
from cynthus.core.event.event_request_decision_event import EventRequestDecisionEvent as Direct
from cynthus.core.system import System
from cynthus.core.test.factory import UserEventFactory, UserFactory

ANSWERS = [
    (EventRequestDecisionAnswer.APPROVED, DecisionEventRequestApprovedEvent),
    (EventRequestDecisionAnswer.APPROVED_CONDITIONALLY, DecisionEventRequestApprovedConditionallyEvent),
    (EventRequestDecisionAnswer.DENIED, DecisionEventRequestDeniedEvent),
    (EventRequestDecisionAnswer.DENIED_CONDITIONALLY, DecisionEventRequestDeniedConditionallyEvent),
]
NOW = datetime(2026, 11, 27, 9, 0, tzinfo=timezone.utc)


def _request(service_id=None, in_reply_to=None):
    requestor = UserFactory()
    event = PartnerServiceListRequestedEvent(
        tenant_id=uuid4(), workspace_id=uuid4(), actor_id=requestor.id_, service_id=service_id,
        action=EventAction.RETRIEVED, data={},
    )

    return EventRequest.model_construct(event=event, requestor=requestor, in_reply_to=in_reply_to)


def _decision(answer, conditions=(), determined_by=None):
    return EventRequestDecision(
        answer=answer, answer_reason='approval_required', conditions=list(conditions), determined_by=determined_by,
        determined_on=NOW,
    )


def test_is_a_signal_event():
    assert issubclass(Direct, SignalEvent)


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.EventRequestDecisionEvent is Direct


def test_declares_its_data_model_and_actions():
    assert Direct.data_model is EventRequestDecisionData
    assert Direct.actions == frozenset({EventAction.CREATED})


class TestDeciding:
    def test_is_a_classmethod(self):
        assert isinstance(Direct.__dict__['deciding'], classmethod)

    @pytest.mark.parametrize('answer, expected', ANSWERS)
    def test_returns_the_matching_subclass(self, answer, expected):
        event = Direct.deciding(_request(), _decision(answer))

        assert type(event) is expected
        assert isinstance(event, Direct)

    @pytest.mark.parametrize('answer, expected', ANSWERS)
    def test_copies_the_ids_and_the_correlation_id(self, answer, expected):
        request = _request(service_id=uuid4())

        event = Direct.deciding(request, _decision(answer))

        assert event.correlation_id == request.event.correlation_id
        assert event.tenant_id == request.event.tenant_id
        assert event.workspace_id == request.event.workspace_id
        assert event.service_id is None
        assert event.actor_id == request.requestor.id_
        assert event.action == EventAction.CREATED

    def test_service_id_argument_is_used(self):
        service_id = uuid4()

        event = Direct.deciding(_request(), _decision(EventRequestDecisionAnswer.APPROVED), service_id=service_id)

        assert event.service_id == service_id

    def test_has_a_new_id_and_a_fresh_time(self):
        request = _request()
        before = datetime.now(timezone.utc)

        first = Direct.deciding(request, _decision(EventRequestDecisionAnswer.APPROVED))
        second = Direct.deciding(request, _decision(EventRequestDecisionAnswer.APPROVED))

        assert first.id_ != request.event.id_
        assert first.id_ != second.id_
        assert before <= first.occurred_on <= datetime.now(timezone.utc)

    def test_data_carries_the_request_and_the_decision(self):
        in_reply_to, service = uuid4(), uuid4()
        request = _request(in_reply_to=in_reply_to)
        decision = _decision(EventRequestDecisionAnswer.APPROVED, determined_by=service)

        data = Direct.deciding(request, decision).parsed_data(EventRequestDecisionData)

        assert data.schema_version == 1
        assert data.event_request_id == request.id_
        assert data.in_reply_to == in_reply_to
        assert data.requested_event_type == 'partner_service_list_requested'
        assert data.requested_action == 'retrieved'
        assert data.requestor_id == request.requestor.id_
        assert data.answer == 'approved'
        assert data.answer_reason == 'approval_required'
        assert data.determined_by == service
        assert data.determined_on == NOW
        assert data.conditions == []

    def test_data_carries_the_conditions(self):
        expires = NOW + timedelta(days=5)
        conditions = [
            DecisionCondition(condition='approval_granted', expires_at=expires),
            DecisionCondition(condition='second'),
        ]

        data = Direct.deciding(
            _request(), _decision(EventRequestDecisionAnswer.APPROVED_CONDITIONALLY, conditions),
        ).parsed_data(EventRequestDecisionData)

        assert [(c.condition, c.status, c.expires_at) for c in data.conditions] == [
            ('approval_granted', 'open', expires), ('second', 'open', None),
        ]

    def test_in_reply_to_none_is_kept(self):
        event = Direct.deciding(_request(), _decision(EventRequestDecisionAnswer.DENIED))

        assert event.parsed_data(EventRequestDecisionData).in_reply_to is None

    def test_a_request_holding_an_event_takes_the_ids_from_its_tenant_workspace_and_user(self):
        event = UserEventFactory(action=EventAction.CREATED)
        request = EventRequest(event=event, requestor=event.user)

        decided = Direct.deciding(request, _decision(EventRequestDecisionAnswer.APPROVED))

        assert type(decided) is DecisionEventRequestApprovedEvent
        assert decided.tenant_id == event.tenant.id_
        assert decided.workspace_id == event.workspace.id_
        assert decided.actor_id == event.user.id_
        assert decided.correlation_id == event.correlation_id
        assert decided.parsed_data(EventRequestDecisionData).requested_action == 'created'

    def test_the_request_and_decision_are_not_changed(self):
        request = _request()
        decision = _decision(EventRequestDecisionAnswer.APPROVED_CONDITIONALLY, [DecisionCondition(condition='x')])
        snapshot = (request.model_dump(), decision.model_dump())

        Direct.deciding(request, decision)

        assert (request.model_dump(), decision.model_dump()) == snapshot

    @pytest.mark.parametrize('kind', ['user', 'system', 'uuid'])
    def test_the_actor_is_the_requestor_not_the_actor_of_the_request_event(self, kind):
        requestor = {'user': UserFactory, 'system': System, 'uuid': uuid4}[kind]()
        request = EventRequest.model_construct(
            id_=uuid4(), requestor=requestor, in_reply_to=None, event=PartnerServiceListRequestedEvent(
                tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=EventAction.RETRIEVED, data={},
            ),
        )
        expected = requestor if kind == 'uuid' else requestor.id_

        event = Direct.deciding(request, _decision(EventRequestDecisionAnswer.APPROVED))

        assert event.actor_id == expected
        assert event.actor_id != request.event.actor_id
        assert event.parsed_data(EventRequestDecisionData).requestor_id == expected

    def test_a_full_event_whose_user_differs_from_the_requestor_gives_the_requestor_as_actor(self):
        event = UserEventFactory(action=EventAction.CREATED)
        requestor = UserFactory()
        request = EventRequest(event=event, requestor=requestor)

        decided = Direct.deciding(request, _decision(EventRequestDecisionAnswer.APPROVED))

        assert requestor.id_ != event.user.id_
        assert decided.actor_id == requestor.id_
        assert decided.tenant_id == event.tenant.id_


class TestValidation:
    def test_action_other_than_created_is_refused(self):
        event = Direct.deciding(_request(), _decision(EventRequestDecisionAnswer.APPROVED))

        for action in [a for a in EventAction if a != EventAction.CREATED]:
            with pytest.raises(ValidationError):
                type(event)(
                    tenant_id=event.tenant_id, workspace_id=event.workspace_id, actor_id=event.actor_id,
                    action=action, data=event.data,
                )

    def test_data_that_is_not_a_decision_is_refused(self):
        with pytest.raises(ValidationError):
            DecisionEventRequestApprovedEvent(
                tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=EventAction.CREATED, data={},
            )


class TestBase:
    @pytest.mark.parametrize('answer', [a.value for a in EventRequestDecisionAnswer])
    def test_the_base_class_accepts_any_answer(self, answer):
        event = Direct.deciding(_request(), _decision(EventRequestDecisionAnswer.APPROVED))

        base = Direct(
            tenant_id=event.tenant_id, workspace_id=event.workspace_id, actor_id=event.actor_id,
            action=EventAction.CREATED, data={**event.data, 'answer': answer},
        )

        assert type(base) is Direct
        assert base.parsed_data(EventRequestDecisionData).answer == answer
