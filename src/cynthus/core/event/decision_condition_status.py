"""Decision Condition Status class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class DecisionConditionStatus(str, Enum):
    """Where a condition of a decision stands"""

    OPEN: str = 'open'
    SATISFIED: str = 'satisfied'
    FAILED: str = 'failed'
    WAIVED: str = 'waived'
    EXPIRED: str = 'expired'
