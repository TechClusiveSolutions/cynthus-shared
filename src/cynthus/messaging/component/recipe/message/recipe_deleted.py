"""RecipeDeleted signal message for the Cynthus project"""

from ....common import PublicRecipeRecipeDeletedSignal, SignalMessage
from ..payload import RecipeDeletedPayload


class RecipeDeletedMessage(SignalMessage[RecipeDeletedPayload]):
    """
        Represents a public.recipe.recipe.deleted signal message

        Emitted by: `cynthus-recipe` when a recipe is deleted.
        Functional Purpose: Lets other services drop what they hold for the recipe.
    """

    event_type: str = PublicRecipeRecipeDeletedSignal.name
