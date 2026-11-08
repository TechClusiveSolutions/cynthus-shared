"""ShoppingListItemUpdated signal message for the Cynthus project"""

from ....common import PublicShoppingListItemUpdatedSignal, SignalMessage
from ..payload import ShoppingListItemUpdatedPayload


class ShoppingListItemUpdatedMessage(SignalMessage[ShoppingListItemUpdatedPayload]):
    """
        Represents a public.shopping_list.item.updated signal message

        Emitted by: `cynthus-shopping`.
        Functional Purpose: Lets other services know which fields of a list item changed.
    """

    event_type: str = PublicShoppingListItemUpdatedSignal.name
