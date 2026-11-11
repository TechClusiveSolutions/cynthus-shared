"""Item Action resource model class for the Cynthus project"""

from enum import Enum


class ItemAction(str, Enum):
    """A list of valid actions that can be performed on an item"""

    CREATED: str = 'created'
    RETRIEVED: str = 'retrieved'
    UPDATED: str = 'updated'
    DELETED: str = 'deleted'
    ADDED: str = 'added'
    REMOVED: str = 'removed'
