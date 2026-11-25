"""Public Partner Signal Base class for the Cynthus project"""

from .base import SignalBase
from .domain_type import SignalDomainType


class PublicPartnerSignalBase(SignalBase, abstract=True):
    """Intermediate base for all public partner signals. Sets the domain component."""

    domain = SignalDomainType.PARTNER
