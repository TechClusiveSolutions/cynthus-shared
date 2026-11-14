"""Public Inventory Shelf Signal Base class for the Cynthus project"""

from .public_inventory_base import PublicInventorySignalBase


class PublicInventoryShelfSignalBase(PublicInventorySignalBase, abstract=True):
    """Intermediate base for all public inventory shelf signals. Sets the aggregate component."""

    aggregate = 'shelf'
