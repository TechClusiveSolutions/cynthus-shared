"""Public Inventory Location Deleted signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_location_base import PublicInventoryLocationSignalBase


class PublicInventoryLocationDeletedSignal(PublicInventoryLocationSignalBase):
    """Concrete signal: public.inventory.location.deleted"""

    action = SignalActionType.DELETED
