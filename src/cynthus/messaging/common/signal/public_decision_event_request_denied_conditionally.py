"""Public Decision Event Request Denied Conditionally signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_decision_event_request_base import PublicDecisionEventRequestSignalBase


class PublicDecisionEventRequestDeniedConditionallySignal(PublicDecisionEventRequestSignalBase):
    """Concrete signal: public.decision.event_request.denied_conditionally"""

    action = SignalActionType.DENIED_CONDITIONALLY
