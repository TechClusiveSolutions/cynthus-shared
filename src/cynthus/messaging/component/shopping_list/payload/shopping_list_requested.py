"""ShoppingListRequestedPayload signal payload class for the Cynthus project"""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from ....common import SignalPayload


class ShoppingListRequestedPayload(SignalPayload):
    """Represents the payload part of a public.shopping_list.list.requested signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    operation: Literal['create', 'get', 'list', 'update', 'delete', 'add_item', 'update_item', 'remove_item', 'check_off_item'] = Field(..., description='What to do with shopping lists or their items')
    resource_id: Optional[str] = Field(default=None, description='The list to get, change or delete, or the list an item belongs to')
    item_id: Optional[str] = Field(default=None, description='The item to change, remove or check off')
    filters: Dict[str, Any] = Field(default_factory=dict, description='Narrows a list of lists, for example q, owner, archived, limit or offset')
    data: Dict[str, Any] = Field(default_factory=dict, description='The fields to create or change a list or an item with')
