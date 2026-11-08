"""Public Shopping List List Updated signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_list_base import PublicShoppingListListSignalBase


class PublicShoppingListListUpdatedSignal(PublicShoppingListListSignalBase):
    """Concrete signal: public.shopping_list.list.updated"""

    action = SignalActionType.UPDATED
