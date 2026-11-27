"""Public Decision Signal Base class for the Cynthus project"""

from .base import SignalBase
from .domain_type import SignalDomainType


class PublicDecisionSignalBase(SignalBase, abstract=True):
    """Intermediate base for all public decision signals. Sets the domain component."""

    domain = SignalDomainType.DECISION
