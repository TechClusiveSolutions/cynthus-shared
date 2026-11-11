"""Event Request Decision Condition class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class EventRequestDecisionCondition(str, Enum):
    """Represents the condition under which   an event request decision can be made"""

    AUTHORIZATION_REQUIRED: str = 'authorization_required'
