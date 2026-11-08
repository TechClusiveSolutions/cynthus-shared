"""RecipeCreated signal message for the Cynthus project"""

from ....common import PublicRecipeRecipeCreatedSignal, SignalMessage
from ..payload import RecipeCreatedPayload


class RecipeCreatedMessage(SignalMessage[RecipeCreatedPayload]):
    """
        Represents a public.recipe.recipe.created signal message

        Emitted by: `cynthus-recipe` when a recipe is created or imported.
        Functional Purpose: Lets other services know a recipe exists and where it came from.
    """

    event_type: str = PublicRecipeRecipeCreatedSignal.name
