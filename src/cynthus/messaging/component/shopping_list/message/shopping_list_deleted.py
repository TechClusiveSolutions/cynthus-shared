"""ShoppingListDeleted signal message for the Cynthus project"""

from ....common import PublicShoppingListListDeletedSignal, SignalMessage
from ..payload import ShoppingListDeletedPayload


class ShoppingListDeletedMessage(SignalMessage[ShoppingListDeletedPayload]):
    """
        Represents a public.shopping_list.list.deleted signal message

        Emitted by: `cynthus-shopping`.
        Functional Purpose: Lets other services know a list was removed; purchase history is kept under the retention policy.
    """

    event_type: str = PublicShoppingListListDeletedSignal.name
