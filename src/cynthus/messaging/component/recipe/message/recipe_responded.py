"""RecipeResponded signal message for the Cynthus project"""

from ....common import PublicRecipeRecipeRespondedSignal, SignalMessage
from ..payload import RecipeRespondedPayload


class RecipeRespondedMessage(SignalMessage[RecipeRespondedPayload]):
    """
        Represents a public.recipe.recipe.responded signal message

        Emitted by: `cynthus-recipe` when it has dealt with a recipe request.
        Functional Purpose: Carries the outcome back to `cynthus-core-api`, which relays it to the caller.
    """

    event_type: str = PublicRecipeRecipeRespondedSignal.name
