"""Item Type resource model class for the Cynthus project"""

from enum import Enum


class ItemType(str, Enum):
    """A list of valid item types"""

    EQUIPMENT: str = 'equipment'
    FOOD: str = 'food'
    SUPPLY: str = 'supply'
