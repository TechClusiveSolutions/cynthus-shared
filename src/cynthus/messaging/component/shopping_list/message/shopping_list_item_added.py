"""ShoppingListItemAdded signal message for the Cynthus project"""

from ....common import PublicShoppingListItemAddedSignal, SignalMessage
from ..payload import ShoppingListItemAddedPayload


class ShoppingListItemAddedMessage(SignalMessage[ShoppingListItemAddedPayload]):
    """
        Represents a public.shopping_list.item.added signal message

        Emitted by: `cynthus-shopping`.
        Functional Purpose: Lets other services know an item was added to a list, by hand or automatically.
    """

    event_type: str = PublicShoppingListItemAddedSignal.name
