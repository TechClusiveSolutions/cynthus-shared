"""Public Decision Event Request Approved signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_decision_event_request_base import PublicDecisionEventRequestSignalBase


class PublicDecisionEventRequestApprovedSignal(PublicDecisionEventRequestSignalBase):
    """Concrete signal: public.decision.event_request.approved"""

    action = SignalActionType.APPROVED
