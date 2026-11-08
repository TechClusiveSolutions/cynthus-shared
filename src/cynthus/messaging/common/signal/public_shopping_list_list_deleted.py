"""Public Shopping List List Deleted signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_list_base import PublicShoppingListListSignalBase


class PublicShoppingListListDeletedSignal(PublicShoppingListListSignalBase):
    """Concrete signal: public.shopping_list.list.deleted"""

    action = SignalActionType.DELETED
