"""Public Shopping List List Signal Base class for the Cynthus project"""

from .public_shopping_list_base import PublicShoppingListSignalBase


class PublicShoppingListListSignalBase(PublicShoppingListSignalBase, abstract=True):
    """Intermediate base for all public shopping list list signals. Sets the aggregate component."""

    aggregate = 'list'
