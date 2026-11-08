"""Public Shopping List Signal Base class for the Cynthus project"""

from .base import SignalBase
from .domain_type import SignalDomainType


class PublicShoppingListSignalBase(SignalBase, abstract=True):
    """Intermediate base for all public shopping list signals. Sets the domain component."""

    domain = SignalDomainType.SHOPPING_LIST
