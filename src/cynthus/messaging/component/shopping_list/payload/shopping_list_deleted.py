"""ShoppingListDeletedPayload signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class ShoppingListDeletedPayload(SignalPayload):
    """Represents the payload part of a public.shopping_list.list.deleted signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    list_id: str = Field(..., description='The identifier of the shopping list')
    owner_id: str = Field(..., description='The identifier of the user who owns the list')
