"""Public Decision Event Request Approved Conditionally signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_decision_event_request_base import PublicDecisionEventRequestSignalBase


class PublicDecisionEventRequestApprovedConditionallySignal(PublicDecisionEventRequestSignalBase):
    """Concrete signal: public.decision.event_request.approved_conditionally"""

    action = SignalActionType.APPROVED_CONDITIONALLY
