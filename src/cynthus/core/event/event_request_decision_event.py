"""Event Request Decision Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, model_validator

from ..system import System
from ..user import User
from .event_action import EventAction
from .event_request import EventRequest
from .event_request_decision import EventRequestDecision
from .event_request_decision_answer import EventRequestDecisionAnswer
from .event_request_decision_data import EventRequestDecisionData
from .signal_event import SignalEvent


class EventRequestDecisionEvent(SignalEvent):
    """
        Represents a decision made on an event request

        A decision is a new fact, so the action is always ``CREATED``. There is one subclass for each answer, because a
        signal generator maps one event class to one signal.
    """

    data_model: ClassVar[type[BaseModel] | None] = EventRequestDecisionData
    actions: ClassVar[frozenset[EventAction] | None] = frozenset({EventAction.CREATED})
    answer: ClassVar[EventRequestDecisionAnswer | None] = None

    @model_validator(mode='after')
    def _validate_answer(self) -> EventRequestDecisionEvent:
        """Check that the answer in ``data`` is the answer this event class stands for"""

        if self.answer is not None and self.data.get('answer') != self.answer.value:
            raise ValueError(
                f'{type(self).__name__} stands for the answer {self.answer.value!r}, not {self.data.get("answer")!r}'
            )

        return self

    @classmethod
    def deciding(
        cls, request: EventRequest, decision: EventRequestDecision, *, service_id: UUID | None = None
    ) -> EventRequestDecisionEvent:
        """
            A new event for ``decision``, made on ``request``

            Returns the subclass that matches ``decision.answer``. Copies the correlation id of the event of the request
            and takes the tenant and workspace ids from it (from its tenant and workspace when it is a full ``Event``).
            The requestor is the actor: the id of a user or system, or the UUID itself. ``service_id`` is the service
            that records the decision.
        """

        from .decision_event_request_approved_conditionally_event import DecisionEventRequestApprovedConditionallyEvent
        from .decision_event_request_approved_event import DecisionEventRequestApprovedEvent
        from .decision_event_request_denied_conditionally_event import DecisionEventRequestDeniedConditionallyEvent
        from .decision_event_request_denied_event import DecisionEventRequestDeniedEvent

        classes = {
            EventRequestDecisionAnswer.APPROVED: DecisionEventRequestApprovedEvent,
            EventRequestDecisionAnswer.APPROVED_CONDITIONALLY: DecisionEventRequestApprovedConditionallyEvent,
            EventRequestDecisionAnswer.DENIED: DecisionEventRequestDeniedEvent,
            EventRequestDecisionAnswer.DENIED_CONDITIONALLY: DecisionEventRequestDeniedConditionallyEvent,
        }
        requested = request.event

        if isinstance(requested, SignalEvent):
            tenant_id = requested.tenant_id
            workspace_id = requested.workspace_id
        else:
            tenant_id = requested.tenant.id_
            workspace_id = requested.workspace.id_

        requestor = request.requestor
        requestor_id = requestor.id_ if isinstance(requestor, (User, System)) else requestor

        # The data is the complete data model in JSON form (ids as text, defaults filled in), exactly what
        # SignalEventReader gives back for the signal of this event, so both events carry equal data
        data = EventRequestDecisionData.from_decision(request, decision).model_dump(mode='json')

        return classes[decision.answer](
            correlation_id=requested.correlation_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            actor_id=requestor_id,
            service_id=service_id,
            action=EventAction.CREATED,
            data=data,
        )
