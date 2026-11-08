"""RecipeRequestedPayload signal payload class for the Cynthus project"""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from ....common import SignalPayload


class RecipeRequestedPayload(SignalPayload):
    """Represents the payload part of a public.recipe.recipe.requested signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    operation: Literal['create', 'get', 'list', 'update', 'delete', 'import_url', 'import_image'] = Field(..., description='What to do with recipes')
    resource_id: Optional[str] = Field(default=None, description='The recipe to get, update or delete')
    filters: Dict[str, Any] = Field(default_factory=dict, description='Narrows a list, for example q, source or owner')
    data: Dict[str, Any] = Field(default_factory=dict, description='The fields to create or change a recipe with; for an import, the url or the upload_id')
