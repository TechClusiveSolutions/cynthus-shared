"""Event Request class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from ..system import System
from ..user import User
from .event import Event
from .signal_event import SignalEvent


class EventRequest(BaseModel):
    """Represents an action requested for a resource"""

    id_: UUID = Field(default_factory=uuid4)
    event: Event | SignalEvent
    requestor: User | System | UUID
    requested_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str | None = None
    in_reply_to: UUID | None = Field(default=None, description='The request this one answers (for example an approval)')

    @property
    def requestor_id(self) -> UUID:
        """The id of whoever asked: a user or the system, or the id itself when the request came from a signal."""

        return self.requestor if isinstance(self.requestor, UUID) else self.requestor.id_
