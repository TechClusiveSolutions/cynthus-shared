"""Inventory Location Created signal message for the Cynthus project"""

from ....common import PublicInventoryLocationCreatedSignal, SignalMessage
from ..payload import InventoryLocationCreatedPayload


class InventoryLocationCreatedMessage(SignalMessage[InventoryLocationCreatedPayload]):
    """
        Represents an inventory location created signal message

        Emitted by: `cynthus-core-api` when a new inventory location is created.
        Functional Purpose: Lets `cynthus-core-cache` and `cynthus-audit` record the new location.
    """

    event_type: str = PublicInventoryLocationCreatedSignal.name
