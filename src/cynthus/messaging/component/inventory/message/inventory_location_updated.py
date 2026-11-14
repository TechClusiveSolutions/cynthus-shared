"""Inventory Location Updated signal message for the Cynthus project"""

from ....common import PublicInventoryLocationUpdatedSignal, SignalMessage
from ..payload import InventoryLocationUpdatedPayload


class InventoryLocationUpdatedMessage(SignalMessage[InventoryLocationUpdatedPayload]):
    """
        Represents an inventory location updated signal message

        Emitted by: `cynthus-core-api` when a location's metadata changes.
        Functional Purpose: Lets `cynthus-core-cache` and `cynthus-audit` refresh the location.
    """

    event_type: str = PublicInventoryLocationUpdatedSignal.name
