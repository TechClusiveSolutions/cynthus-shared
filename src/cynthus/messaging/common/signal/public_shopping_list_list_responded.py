"""Public Shopping List List Responded signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_shopping_list_list_base import PublicShoppingListListSignalBase


class PublicShoppingListListRespondedSignal(PublicShoppingListListSignalBase):
    """Concrete signal: public.shopping_list.list.responded"""

    action = SignalActionType.RESPONDED
