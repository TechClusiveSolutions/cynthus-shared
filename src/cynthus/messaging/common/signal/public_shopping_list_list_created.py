"""Public Shopping List List Created signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_list_base import PublicShoppingListListSignalBase


class PublicShoppingListListCreatedSignal(PublicShoppingListListSignalBase):
    """Concrete signal: public.shopping_list.list.created"""

    action = SignalActionType.CREATED
