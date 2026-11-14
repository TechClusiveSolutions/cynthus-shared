"""Inventory Item Added signal message for the Cynthus project"""

from ....common import PublicInventoryItemAddedSignal, SignalMessage
from ..payload import InventoryItemAddedPayload


class InventoryItemAddedMessage(SignalMessage[InventoryItemAddedPayload]):
    """
        Represents an inventory item added signal message

        Emitted by: `cynthus-core-api` when an item is added to a shelf.
        Functional Purpose: Lets `cynthus-core-cache` update the snapshot and `cynthus-scheduler` register an expiry watch.
    """

    event_type: str = PublicInventoryItemAddedSignal.name
