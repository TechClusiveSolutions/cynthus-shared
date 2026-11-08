"""ShoppingListItemCheckedOffPayload signal payload class for the Cynthus project"""

from typing import Optional

from pydantic import Field

from ....common import SignalPayload


class ShoppingListItemCheckedOffPayload(SignalPayload):
    """Represents the payload part of a public.shopping_list.item.checked_off signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    list_id: str = Field(..., description='The identifier of the shopping list')
    item_id: str = Field(..., description='The identifier of the list item')
    name: str = Field(..., description='What the item or list is called')
    quantity_purchased: Optional[float] = Field(default=None, gt=0, description='How much was actually bought')
    unit: Optional[str] = Field(default=None, description='The unit code of the quantity bought')
    provider_id: Optional[str] = Field(default=None, description='The store or vendor it was bought from')
