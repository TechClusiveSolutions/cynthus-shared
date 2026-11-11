"""Item resource model class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .item_action import ItemAction
from .item_brand import ItemBrand
from .item_type import ItemType
from .resource import Resource


class Item(Resource):
    """Represents an item resource"""

    type: ItemType
    brand: ItemBrand | None = None
    barcode: str | None = None
    expiration_date: datetime | None = None
    action: ItemAction | None = Field(default=None, description='An action taken on an item')
