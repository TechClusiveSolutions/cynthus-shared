"""Public Inventory Item Added signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_item_base import PublicInventoryItemSignalBase


class PublicInventoryItemAddedSignal(PublicInventoryItemSignalBase):
    """Concrete signal: public.inventory.item.added"""

    action = SignalActionType.ADDED
