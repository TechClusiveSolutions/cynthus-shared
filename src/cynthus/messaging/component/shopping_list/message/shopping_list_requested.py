"""ShoppingListRequested signal message for the Cynthus project"""

from ....common import PublicShoppingListListRequestedSignal, SignalMessage
from ..payload import ShoppingListRequestedPayload


class ShoppingListRequestedMessage(SignalMessage[ShoppingListRequestedPayload]):
    """
        Represents a public.shopping_list.list.requested signal message

        Emitted by: `cynthus-core-api` when a caller asks to create, get, list, update or delete a shopping list, or to add, change, remove or check off one of its items.
        Functional Purpose: Hands the request to the Shopping service so the caller gets an immediate acknowledgement.
    """

    event_type: str = PublicShoppingListListRequestedSignal.name
