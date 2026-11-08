"""ShoppingListUpdatedPayload signal payload class for the Cynthus project"""

from typing import List

from pydantic import Field

from ....common import SignalPayload


class ShoppingListUpdatedPayload(SignalPayload):
    """Represents the payload part of a public.shopping_list.list.updated signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    list_id: str = Field(..., description='The identifier of the shopping list')
    owner_id: str = Field(..., description='The identifier of the user who owns the list')
    changed: List[str] = Field(default_factory=list, description='The fields that changed')
