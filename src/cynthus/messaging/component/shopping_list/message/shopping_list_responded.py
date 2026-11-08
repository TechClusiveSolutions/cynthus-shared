"""ShoppingListResponded signal message for the Cynthus project"""

from ....common import PublicShoppingListListRespondedSignal, SignalMessage
from ..payload import ShoppingListRespondedPayload


class ShoppingListRespondedMessage(SignalMessage[ShoppingListRespondedPayload]):
    """
        Represents a public.shopping_list.list.responded signal message

        Emitted by: `cynthus-shopping` when it has dealt with a shopping list request.
        Functional Purpose: Carries the outcome back to `cynthus-core-api`, which relays it to the caller.
    """

    event_type: str = PublicShoppingListListRespondedSignal.name
