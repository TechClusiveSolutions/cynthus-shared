"""Public Shopping List Item Signal Base class for the Cynthus project"""

from .public_shopping_list_base import PublicShoppingListSignalBase


class PublicShoppingListItemSignalBase(PublicShoppingListSignalBase, abstract=True):
    """Intermediate base for all public shopping list item signals. Sets the aggregate component."""

    aggregate = 'item'
