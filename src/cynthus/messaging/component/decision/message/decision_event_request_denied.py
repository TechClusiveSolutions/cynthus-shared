"""Decision Event Request Denied signal message for the Cynthus project"""

from ....common import PublicDecisionEventRequestDeniedSignal, SignalMessage
from ..payload import EventRequestDecisionPayload


class DecisionEventRequestDeniedMessage(SignalMessage[EventRequestDecisionPayload]):
    """
        Represents a decision event request denied signal message

        Emitted by: the service that decides an event request (ADR-013).
        Functional Purpose: Publishes the decision as a fact so the audit engine and any subscriber see it as it happens.
    """

    event_type: str = PublicDecisionEventRequestDeniedSignal.name
