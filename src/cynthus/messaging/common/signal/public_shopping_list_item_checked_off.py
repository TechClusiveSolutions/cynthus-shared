"""Public Shopping List Item CheckedOff signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_item_base import PublicShoppingListItemSignalBase


class PublicShoppingListItemCheckedOffSignal(PublicShoppingListItemSignalBase):
    """Concrete signal: public.shopping_list.item.checked_off"""

    action = SignalActionType.CHECKED_OFF
