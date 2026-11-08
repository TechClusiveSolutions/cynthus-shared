"""RecipeUpdated signal message for the Cynthus project"""

from ....common import PublicRecipeRecipeUpdatedSignal, SignalMessage
from ..payload import RecipeUpdatedPayload


class RecipeUpdatedMessage(SignalMessage[RecipeUpdatedPayload]):
    """
        Represents a public.recipe.recipe.updated signal message

        Emitted by: `cynthus-recipe` when a recipe is changed.
        Functional Purpose: Lets other services know which fields of a recipe changed.
    """

    event_type: str = PublicRecipeRecipeUpdatedSignal.name
