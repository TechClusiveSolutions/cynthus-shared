"""User Event class for the Cynthus project"""

from __future__ import annotations

from .event import Event

from ..user import User


class UserEvent(Event):
    """Represents an action taken on a resource by a User"""

    user: User
