"""Inventory Event Request class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field

from .event_request import EventRequest

from ..system import System
from ..user import User


class InventoryEventRequest(EventRequest):
    """Represents an action requested for an inventory resource"""
