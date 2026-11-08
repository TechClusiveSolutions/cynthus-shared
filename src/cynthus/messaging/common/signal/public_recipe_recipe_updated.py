"""Public Recipe Recipe Updated signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_recipe_recipe_base import PublicRecipeRecipeSignalBase


class PublicRecipeRecipeUpdatedSignal(PublicRecipeRecipeSignalBase):
    """Concrete signal: public.recipe.recipe.updated"""

    action = SignalActionType.UPDATED
