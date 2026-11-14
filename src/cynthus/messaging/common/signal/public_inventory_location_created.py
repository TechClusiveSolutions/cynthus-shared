"""Public Inventory Location Created signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_location_base import PublicInventoryLocationSignalBase


class PublicInventoryLocationCreatedSignal(PublicInventoryLocationSignalBase):
    """Concrete signal: public.inventory.location.created"""

    action = SignalActionType.CREATED
