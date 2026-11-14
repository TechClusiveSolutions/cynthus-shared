"""Inventory Item Updated signal message for the Cynthus project"""

from ....common import PublicInventoryItemUpdatedSignal, SignalMessage
from ..payload import InventoryItemUpdatedPayload


class InventoryItemUpdatedMessage(SignalMessage[InventoryItemUpdatedPayload]):
    """
        Represents an inventory item updated signal message

        Emitted by: `cynthus-core-api` when an item's quantity or metadata changes.
        Functional Purpose: Lets `cynthus-core-cache` and `cynthus-scheduler` refresh the item and its expiry watch.
    """

    event_type: str = PublicInventoryItemUpdatedSignal.name
