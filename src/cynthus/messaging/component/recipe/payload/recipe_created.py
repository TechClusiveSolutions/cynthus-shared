"""RecipeCreatedPayload signal payload class for the Cynthus project"""

from typing import Optional

from pydantic import Field

from ....common import SignalPayload


class RecipeCreatedPayload(SignalPayload):
    """Represents the payload part of a public.recipe.recipe.created signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    recipe_id: str = Field(..., description='The identifier of the recipe')
    owner_id: str = Field(..., description='The identifier of the user who owns the recipe')
    source: str = Field(..., description='Where the recipe came from: manual, web or image')
    source_url: Optional[str] = Field(default=None, description='The page the recipe was imported from')
