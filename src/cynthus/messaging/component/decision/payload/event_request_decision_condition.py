"""Event Request Decision Condition model for the Cynthus project"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EventRequestDecisionConditionPayload(BaseModel):
    """One condition of a decision: what a reply must carry, where it stands and when it expires"""

    condition: str = Field(..., description='The answer reason a reply must carry to meet the condition')
    status: str = Field(..., description='open, satisfied, failed, waived or expired')
    expires_at: Optional[datetime] = Field(default=None, description='When an open condition expires; empty means never')
