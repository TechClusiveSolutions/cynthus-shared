"""RecipeRespondedPayload signal payload class for the Cynthus project"""

from typing import Any, Optional

from pydantic import Field

from ....common import SignalPayload


class RecipeRespondedPayload(SignalPayload):
    """Represents the payload part of a public.recipe.recipe.responded signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    operation: str = Field(..., description='The operation that was requested')
    status: int = Field(..., description='200, 201 or 204 when it worked; 401, 403, 404, 405, 409, 422, 502 or 503 when it did not')
    result: Optional[Any] = Field(default=None, description='The recipe, or the list of recipes, when it worked')
    error: Optional[str] = Field(default=None, description='Why the request failed')
