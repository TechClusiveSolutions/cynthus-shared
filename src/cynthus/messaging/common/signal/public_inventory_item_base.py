"""Public Inventory Item Signal Base class for the Cynthus project"""

from .public_inventory_base import PublicInventorySignalBase


class PublicInventoryItemSignalBase(PublicInventorySignalBase, abstract=True):
    """Intermediate base for all public inventory item signals. Sets the aggregate component."""

    aggregate = 'item'
