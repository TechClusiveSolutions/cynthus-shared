"""ShoppingListCreatedPayload signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class ShoppingListCreatedPayload(SignalPayload):
    """Represents the payload part of a public.shopping_list.list.created signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    list_id: str = Field(..., description='The identifier of the shopping list')
    owner_id: str = Field(..., description='The identifier of the user who owns the list')
    name: str = Field(..., description='The name of the list')
    is_procurement_target: bool = Field(default=False, description='Whether the list receives items added automatically from low stock')
