"""Public Inventory Shelf Updated signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_shelf_base import PublicInventoryShelfSignalBase


class PublicInventoryShelfUpdatedSignal(PublicInventoryShelfSignalBase):
    """Concrete signal: public.inventory.shelf.updated"""

    action = SignalActionType.UPDATED
