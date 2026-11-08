"""RecipeUpdatedPayload signal payload class for the Cynthus project"""

from typing import List

from pydantic import Field

from ....common import SignalPayload


class RecipeUpdatedPayload(SignalPayload):
    """Represents the payload part of a public.recipe.recipe.updated signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    recipe_id: str = Field(..., description='The identifier of the recipe')
    owner_id: str = Field(..., description='The identifier of the user who owns the recipe')
    changed: List[str] = Field(default_factory=list, description='The fields that changed')
