"""Public Inventory Shelf Deleted signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_shelf_base import PublicInventoryShelfSignalBase


class PublicInventoryShelfDeletedSignal(PublicInventoryShelfSignalBase):
    """Concrete signal: public.inventory.shelf.deleted"""

    action = SignalActionType.DELETED
