"""ShoppingListCreated signal message for the Cynthus project"""

from ....common import PublicShoppingListListCreatedSignal, SignalMessage
from ..payload import ShoppingListCreatedPayload


class ShoppingListCreatedMessage(SignalMessage[ShoppingListCreatedPayload]):
    """
        Represents a public.shopping_list.list.created signal message

        Emitted by: `cynthus-shopping`.
        Functional Purpose: Lets other services know a shopping list exists and whether it is the workspace procurement target.
    """

    event_type: str = PublicShoppingListListCreatedSignal.name
