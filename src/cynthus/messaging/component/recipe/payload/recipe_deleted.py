"""RecipeDeletedPayload signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class RecipeDeletedPayload(SignalPayload):
    """Represents the payload part of a public.recipe.recipe.deleted signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    recipe_id: str = Field(..., description='The identifier of the recipe')
    owner_id: str = Field(..., description='The identifier of the user who owned the recipe')
