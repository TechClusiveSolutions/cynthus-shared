"""Public Decision Event Request Denied signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_decision_event_request_base import PublicDecisionEventRequestSignalBase


class PublicDecisionEventRequestDeniedSignal(PublicDecisionEventRequestSignalBase):
    """Concrete signal: public.decision.event_request.denied"""

    action = SignalActionType.DENIED
