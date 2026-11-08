"""RecipeRequested signal message for the Cynthus project"""

from ....common import PublicRecipeRecipeRequestedSignal, SignalMessage
from ..payload import RecipeRequestedPayload


class RecipeRequestedMessage(SignalMessage[RecipeRequestedPayload]):
    """
        Represents a public.recipe.recipe.requested signal message

        Emitted by: `cynthus-core-api` when a caller asks to create, get, list, update or delete a recipe, or to import one from a web page or an uploaded image.
        Functional Purpose: Hands the request to the Recipe service so the caller gets an immediate acknowledgement.
    """

    event_type: str = PublicRecipeRecipeRequestedSignal.name
