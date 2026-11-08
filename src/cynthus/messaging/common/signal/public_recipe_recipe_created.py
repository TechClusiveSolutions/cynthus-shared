"""Public Recipe Recipe Created signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_recipe_recipe_base import PublicRecipeRecipeSignalBase


class PublicRecipeRecipeCreatedSignal(PublicRecipeRecipeSignalBase):
    """Concrete signal: public.recipe.recipe.created"""

    action = SignalActionType.CREATED
