"""Decision Event Request Approved Conditionally signal message for the Cynthus project"""

from ....common import PublicDecisionEventRequestApprovedConditionallySignal, SignalMessage
from ..payload import EventRequestDecisionPayload


class DecisionEventRequestApprovedConditionallyMessage(SignalMessage[EventRequestDecisionPayload]):
    """
        Represents a decision event request approved conditionally signal message

        Emitted by: the service that decides an event request (ADR-013).
        Functional Purpose: Publishes the decision, with the conditions it waits for, so the audit engine and any subscriber see it.
    """

    event_type: str = PublicDecisionEventRequestApprovedConditionallySignal.name
