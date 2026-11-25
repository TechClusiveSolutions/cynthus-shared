"""Public Inventory Location Signal Base class for the Cynthus project"""

from .public_inventory_base import PublicInventorySignalBase


class PublicInventoryLocationSignalBase(PublicInventorySignalBase, abstract=True):
    """Intermediate base for all public inventory location signals. Sets the aggregate component."""

    aggregate = 'location'
