"""Event Action class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class EventAction(str, Enum):
    """Represents an action that can be taken on a resource"""

    ADDED: str = 'added'
    REMOVED: str = 'removed'
    CREATED: str = 'created'
    RETRIEVED: str = 'retrieved'
    UPDATED: str = 'updated'
    DELETED: str = 'deleted'
