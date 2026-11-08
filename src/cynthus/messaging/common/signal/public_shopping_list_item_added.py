"""Public Shopping List Item Added signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_item_base import PublicShoppingListItemSignalBase


class PublicShoppingListItemAddedSignal(PublicShoppingListItemSignalBase):
    """Concrete signal: public.shopping_list.item.added"""

    action = SignalActionType.ADDED
