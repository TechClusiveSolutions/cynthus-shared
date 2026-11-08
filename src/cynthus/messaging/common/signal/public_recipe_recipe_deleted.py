"""Public Recipe Recipe Deleted signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_recipe_recipe_base import PublicRecipeRecipeSignalBase


class PublicRecipeRecipeDeletedSignal(PublicRecipeRecipeSignalBase):
    """Concrete signal: public.recipe.recipe.deleted"""

    action = SignalActionType.DELETED
