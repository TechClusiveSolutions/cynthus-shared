"""Public Recipe Recipe Requested signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_recipe_recipe_base import PublicRecipeRecipeSignalBase


class PublicRecipeRecipeRequestedSignal(PublicRecipeRecipeSignalBase):
    """Concrete signal: public.recipe.recipe.requested"""

    action = SignalActionType.REQUESTED
