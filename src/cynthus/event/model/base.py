"""Event Base model class for the Cynthus project"""

from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from typing import Any, Optional
from uuid import UUID, uuid4


class EventBase(BaseModel):
    event_id: UUID = Field(
        default_factory=uuid4,
        description='The id of the event'
    )

    event_type: str = field(
        ...,
        description='The type of the event'
    )

    event_time: datetime = Field(
        default_factory=lambda : datetime.now(timezone.utc),
        description='The date and time the event occurred'
    )

    system: str = Field(
        ...,
        description='A string indicating which system produced this event',
    )

    correlation_id: Optional[UUID] = Field(
        default=None,
        description='A UUID value indicating a correlation between various events'
    )

    data: Optional[dict[str, Any]] = Field(
        default=None,
        description='A dictionary containing the data of the event'
    )
