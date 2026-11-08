"""ShoppingListItemCheckedOff signal message for the Cynthus project"""

from ....common import PublicShoppingListItemCheckedOffSignal, SignalMessage
from ..payload import ShoppingListItemCheckedOffPayload


class ShoppingListItemCheckedOffMessage(SignalMessage[ShoppingListItemCheckedOffPayload]):
    """
        Represents a public.shopping_list.item.checked_off signal message

        Emitted by: `cynthus-shopping`.
        Functional Purpose: Lets other services know the requester bought the item in person; feeds the purchase history.
    """

    event_type: str = PublicShoppingListItemCheckedOffSignal.name
