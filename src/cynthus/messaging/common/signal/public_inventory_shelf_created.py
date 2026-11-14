"""Public Inventory Shelf Created signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_shelf_base import PublicInventoryShelfSignalBase


class PublicInventoryShelfCreatedSignal(PublicInventoryShelfSignalBase):
    """Concrete signal: public.inventory.shelf.created"""

    action = SignalActionType.CREATED
