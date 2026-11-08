"""Public Shopping List List Requested signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_list_base import PublicShoppingListListSignalBase


class PublicShoppingListListRequestedSignal(PublicShoppingListListSignalBase):
    """Concrete signal: public.shopping_list.list.requested"""

    action = SignalActionType.REQUESTED
