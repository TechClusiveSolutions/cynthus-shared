"""User Event class for the Cynthus project"""

from __future__ import annotations

from ..user import User
from .event import Event


class UserEvent(Event):
    """Represents an action taken on a resource by a User"""

    user: User
