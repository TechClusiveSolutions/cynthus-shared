"""Public Shopping List Item Removed signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_item_base import PublicShoppingListItemSignalBase


class PublicShoppingListItemRemovedSignal(PublicShoppingListItemSignalBase):
    """Concrete signal: public.shopping_list.item.removed"""

    action = SignalActionType.REMOVED
