"""Decision Event Request Denied Conditionally signal message for the Cynthus project"""

from ....common import PublicDecisionEventRequestDeniedConditionallySignal, SignalMessage
from ..payload import EventRequestDecisionPayload


class DecisionEventRequestDeniedConditionallyMessage(SignalMessage[EventRequestDecisionPayload]):
    """
        Represents a decision event request denied conditionally signal message

        Emitted by: the service that decides an event request (ADR-013).
        Functional Purpose: Publishes a denial that holds unless the listed conditions are met, so the audit engine and any subscriber see it.
    """

    event_type: str = PublicDecisionEventRequestDeniedConditionallySignal.name
