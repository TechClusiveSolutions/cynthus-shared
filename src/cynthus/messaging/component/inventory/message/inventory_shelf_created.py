"""Inventory Shelf Created signal message for the Cynthus project"""

from ....common import PublicInventoryShelfCreatedSignal, SignalMessage
from ..payload import InventoryShelfCreatedPayload


class InventoryShelfCreatedMessage(SignalMessage[InventoryShelfCreatedPayload]):
    """
        Represents an inventory shelf created signal message

        Emitted by: `cynthus-core-api` when a new shelf is added to a location.
        Functional Purpose: Lets `cynthus-core-cache` and `cynthus-audit` record the new shelf.
    """

    event_type: str = PublicInventoryShelfCreatedSignal.name
