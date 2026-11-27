"""Decision Signal Generator class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .....core.event import (
    DecisionEventRequestApprovedConditionallyEvent,
    DecisionEventRequestApprovedEvent,
    DecisionEventRequestDeniedConditionallyEvent,
    DecisionEventRequestDeniedEvent,
    EventRequestDecisionData,
    EventRequestDecisionEvent,
)
from ....common.signal.lifecycle_action import LifecycleAction
from ....common.signal.public_decision_event_request_approved import PublicDecisionEventRequestApprovedSignal
from ....common.signal.public_decision_event_request_approved_conditionally import (
    PublicDecisionEventRequestApprovedConditionallySignal,
)
from ....common.signal.public_decision_event_request_denied import PublicDecisionEventRequestDeniedSignal
from ....common.signal.public_decision_event_request_denied_conditionally import (
    PublicDecisionEventRequestDeniedConditionallySignal,
)
from ....generator import SignalContract, SignalGenerator
from ..message import (
    DecisionEventRequestApprovedConditionallyMessage,
    DecisionEventRequestApprovedMessage,
    DecisionEventRequestDeniedConditionallyMessage,
    DecisionEventRequestDeniedMessage,
)
from ..payload import EventRequestDecisionConditionPayload, EventRequestDecisionPayload

SOURCES = {
    'schema_version': 'data.schema_version',
    'event_request_id': 'data.event_request_id',
    'in_reply_to': 'data.in_reply_to',
    'requested_event_type': 'data.requested_event_type',
    'requested_action': 'data.requested_action',
    'requestor_id': 'data.requestor_id',
    'answer': 'data.answer',
    'answer_reason': 'data.answer_reason',
    'conditions': 'data.conditions',
    'determined_by': 'data.determined_by',
    'determined_on': 'data.determined_on',
}


class DecisionSignalGenerator(SignalGenerator):
    """Generates the four signals that publish the decisions made on event requests"""

    contracts: ClassVar[tuple[SignalContract, ...]] = (
        SignalContract(
            features=('FT-AC-002',),
            event='DecisionEventRequestApprovedEvent',
            signal=PublicDecisionEventRequestApprovedSignal,
            message=DecisionEventRequestApprovedMessage,
            payload=EventRequestDecisionPayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='approved',
            sources=SOURCES,
        ),
        SignalContract(
            features=('FT-AC-002',),
            event='DecisionEventRequestApprovedConditionallyEvent',
            signal=PublicDecisionEventRequestApprovedConditionallySignal,
            message=DecisionEventRequestApprovedConditionallyMessage,
            payload=EventRequestDecisionPayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='approved_conditionally',
            sources=SOURCES,
        ),
        SignalContract(
            features=('FT-AC-002',),
            event='DecisionEventRequestDeniedEvent',
            signal=PublicDecisionEventRequestDeniedSignal,
            message=DecisionEventRequestDeniedMessage,
            payload=EventRequestDecisionPayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='denied',
            sources=SOURCES,
        ),
        SignalContract(
            features=('FT-AC-002',),
            event='DecisionEventRequestDeniedConditionallyEvent',
            signal=PublicDecisionEventRequestDeniedConditionallySignal,
            message=DecisionEventRequestDeniedConditionallyMessage,
            payload=EventRequestDecisionPayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='denied_conditionally',
            sources=SOURCES,
        ),
    )

    def approved(self, event: DecisionEventRequestApprovedEvent) -> DecisionEventRequestApprovedMessage:
        """The message for an approval, from the data of the event"""

        return self._message(event, 'approved')

    def approved_conditionally(
        self, event: DecisionEventRequestApprovedConditionallyEvent
    ) -> DecisionEventRequestApprovedConditionallyMessage:
        """The message for an approval that waits for conditions, from the data of the event"""

        return self._message(event, 'approved_conditionally')

    def denied(self, event: DecisionEventRequestDeniedEvent) -> DecisionEventRequestDeniedMessage:
        """The message for a denial, from the data of the event"""

        return self._message(event, 'denied')

    def denied_conditionally(
        self, event: DecisionEventRequestDeniedConditionallyEvent
    ) -> DecisionEventRequestDeniedConditionallyMessage:
        """The message for a denial that holds unless conditions are met, from the data of the event"""

        return self._message(event, 'denied_conditionally')

    def _message(self, event: EventRequestDecisionEvent, method: str):
        contract = self.contract(method)
        data = event.parsed_data(EventRequestDecisionData)
        payload = EventRequestDecisionPayload(
            schema_version=data.schema_version,
            event_request_id=data.event_request_id,
            in_reply_to=data.in_reply_to,
            requested_event_type=data.requested_event_type,
            requested_action=data.requested_action,
            requestor_id=data.requestor_id,
            answer=data.answer,
            answer_reason=data.answer_reason,
            conditions=[
                EventRequestDecisionConditionPayload(condition=c.condition, status=c.status, expires_at=c.expires_at)
                for c in data.conditions
            ],
            determined_by=data.determined_by,
            determined_on=data.determined_on,
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)
