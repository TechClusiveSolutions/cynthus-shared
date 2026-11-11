"""Inventory Event class for the Cynthus project"""

from __future__ import annotations

from pydantic import Field

from .user_event import UserEvent


class InventoryEvent(UserEvent):
    """Represents an action taken on an inventory resource"""
