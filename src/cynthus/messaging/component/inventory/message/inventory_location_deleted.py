"""Inventory Location Deleted signal message for the Cynthus project"""

from ....common import PublicInventoryLocationDeletedSignal, SignalMessage
from ..payload import InventoryLocationDeletedPayload


class InventoryLocationDeletedMessage(SignalMessage[InventoryLocationDeletedPayload]):
    """
        Represents an inventory location deleted signal message

        Emitted by: `cynthus-core-api` when a location is removed.
        Functional Purpose: Lets `cynthus-shopping` clear procurement links and `cynthus-core-cache` drop the location.
    """

    event_type: str = PublicInventoryLocationDeletedSignal.name
