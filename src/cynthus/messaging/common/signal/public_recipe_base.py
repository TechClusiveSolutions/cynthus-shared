"""Public Recipe Signal Base class for the Cynthus project"""

from .base import SignalBase
from .domain_type import SignalDomainType


class PublicRecipeSignalBase(SignalBase, abstract=True):
    """Intermediate base for all public recipe signals. Sets the domain component."""

    domain = SignalDomainType.RECIPE
