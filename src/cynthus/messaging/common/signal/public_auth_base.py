"""Public Auth Signal Base class for the Cynthus project"""

from .base import SignalBase
from .domain_type import SignalDomainType


class PublicAuthSignalBase(SignalBase, abstract=True):
    """Intermediate base for all public auth signals. Sets the domain component."""

    domain = SignalDomainType.AUTH
