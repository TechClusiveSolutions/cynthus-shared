"""Inventory Shelf Deleted signal message for the Cynthus project"""

from ....common import PublicInventoryShelfDeletedSignal, SignalMessage
from ..payload import InventoryShelfDeletedPayload


class InventoryShelfDeletedMessage(SignalMessage[InventoryShelfDeletedPayload]):
    """
        Represents an inventory shelf deleted signal message

        Emitted by: `cynthus-core-api` when a shelf is removed.
        Functional Purpose: Lets `cynthus-core-cache` drop the shelf and its items.
    """

    event_type: str = PublicInventoryShelfDeletedSignal.name
