"""Public Recipe Recipe Responded signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_recipe_recipe_base import PublicRecipeRecipeSignalBase


class PublicRecipeRecipeRespondedSignal(PublicRecipeRecipeSignalBase):
    """Concrete signal: public.recipe.recipe.responded"""

    action = SignalActionType.RESPONDED
