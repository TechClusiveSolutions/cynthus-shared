"""Public Inventory Location Updated signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_inventory_location_base import PublicInventoryLocationSignalBase


class PublicInventoryLocationUpdatedSignal(PublicInventoryLocationSignalBase):
    """Concrete signal: public.inventory.location.updated"""

    action = SignalActionType.UPDATED
