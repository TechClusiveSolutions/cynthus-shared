"""ShoppingListItemRemovedPayload signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class ShoppingListItemRemovedPayload(SignalPayload):
    """Represents the payload part of a public.shopping_list.item.removed signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    list_id: str = Field(..., description='The identifier of the shopping list')
    item_id: str = Field(..., description='The identifier of the list item')
