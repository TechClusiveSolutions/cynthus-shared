"""Public Inventory Item Removed signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_item_base import PublicInventoryItemSignalBase


class PublicInventoryItemRemovedSignal(PublicInventoryItemSignalBase):
    """Concrete signal: public.inventory.item.removed"""

    action = SignalActionType.REMOVED
