"""Public Shopping List Item Updated signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_item_base import PublicShoppingListItemSignalBase


class PublicShoppingListItemUpdatedSignal(PublicShoppingListItemSignalBase):
    """Concrete signal: public.shopping_list.item.updated"""

    action = SignalActionType.UPDATED
