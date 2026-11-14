"""Inventory Shelf Updated signal message for the Cynthus project"""

from ....common import PublicInventoryShelfUpdatedSignal, SignalMessage
from ..payload import InventoryShelfUpdatedPayload


class InventoryShelfUpdatedMessage(SignalMessage[InventoryShelfUpdatedPayload]):
    """
        Represents an inventory shelf updated signal message

        Emitted by: `cynthus-core-api` when a shelf's metadata changes.
        Functional Purpose: Lets `cynthus-core-cache` and `cynthus-audit` refresh the shelf.
    """

    event_type: str = PublicInventoryShelfUpdatedSignal.name
