"""Event Request class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional

from .event import Event

from ..system import System
from ..user import User


class EventRequest(BaseModel):
    """Represents an action requested for a resource"""

    event: Event
    requestor: User | System
    requested_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str | None = None
