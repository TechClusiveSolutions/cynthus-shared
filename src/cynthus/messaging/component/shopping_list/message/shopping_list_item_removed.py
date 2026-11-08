"""ShoppingListItemRemoved signal message for the Cynthus project"""

from ....common import PublicShoppingListItemRemovedSignal, SignalMessage
from ..payload import ShoppingListItemRemovedPayload


class ShoppingListItemRemovedMessage(SignalMessage[ShoppingListItemRemovedPayload]):
    """
        Represents a public.shopping_list.item.removed signal message

        Emitted by: `cynthus-shopping`.
        Functional Purpose: Lets other services know an item left the list without being bought.
    """

    event_type: str = PublicShoppingListItemRemovedSignal.name
