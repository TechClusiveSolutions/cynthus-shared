"""Event Request Decision Condition Data class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventRequestDecisionConditionData(BaseModel):
    """One condition of a decision, as the data of an event request decision event"""

    model_config = ConfigDict(extra='forbid')

    condition: str
    status: str
    expires_at: datetime | None = None
