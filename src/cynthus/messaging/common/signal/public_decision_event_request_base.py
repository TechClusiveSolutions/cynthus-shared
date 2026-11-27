"""Public Decision Event Request Signal Base class for the Cynthus project"""

from .public_decision_base import PublicDecisionSignalBase


class PublicDecisionEventRequestSignalBase(PublicDecisionSignalBase, abstract=True):
    """Intermediate base for all public decision event request signals. Sets the aggregate component."""

    aggregate = 'event_request'
