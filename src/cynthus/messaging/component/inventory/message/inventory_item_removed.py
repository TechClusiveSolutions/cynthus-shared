"""Inventory Item Removed signal message for the Cynthus project"""

from ....common import PublicInventoryItemRemovedSignal, SignalMessage
from ..payload import InventoryItemRemovedPayload


class InventoryItemRemovedMessage(SignalMessage[InventoryItemRemovedPayload]):
    """
        Represents an inventory item removed signal message

        Emitted by: `cynthus-core-api` when an item is removed from a shelf.
        Functional Purpose: Lets `cynthus-core-cache` drop the item and `cynthus-scheduler` cancel its expiry watch.
    """

    event_type: str = PublicInventoryItemRemovedSignal.name
