"""ShoppingListUpdated signal message for the Cynthus project"""

from ....common import PublicShoppingListListUpdatedSignal, SignalMessage
from ..payload import ShoppingListUpdatedPayload


class ShoppingListUpdatedMessage(SignalMessage[ShoppingListUpdatedPayload]):
    """
        Represents a public.shopping_list.list.updated signal message

        Emitted by: `cynthus-shopping`.
        Functional Purpose: Lets other services know which fields of a list changed, including archiving it.
    """

    event_type: str = PublicShoppingListListUpdatedSignal.name
