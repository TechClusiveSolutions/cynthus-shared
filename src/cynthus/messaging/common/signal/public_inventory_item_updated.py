"""Public Inventory Item Updated signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_item_base import PublicInventoryItemSignalBase


class PublicInventoryItemUpdatedSignal(PublicInventoryItemSignalBase):
    """Concrete signal: public.inventory.item.updated"""

    action = SignalActionType.UPDATED
