"""ShoppingListItemAddedPayload signal payload class for the Cynthus project"""

from typing import Optional

from pydantic import Field

from ....common import SignalPayload


class ShoppingListItemAddedPayload(SignalPayload):
    """Represents the payload part of a public.shopping_list.item.added signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    list_id: str = Field(..., description='The identifier of the shopping list')
    item_id: str = Field(..., description='The identifier of the list item')
    name: str = Field(..., description='What the item or list is called')
    quantity: Optional[float] = Field(default=None, gt=0, description='How much was asked for')
    unit: Optional[str] = Field(default=None, description='The unit code of the quantity')
    notes: Optional[str] = Field(default=None, description='The requester notes for the item')
    source: str = Field(default='manual', description='How the item got on the list: manual, low_stock, generated or meal_gap')
    catalog_item_id: Optional[str] = Field(default=None, description='The catalog product the item refers to')
    inventory_item_id: Optional[str] = Field(default=None, description='The inventory item that ran low, when the item came from low stock')
