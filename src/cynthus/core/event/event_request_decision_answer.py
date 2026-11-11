"""Event Request Decision Answer class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class EventRequestDecisionAnswer(str, Enum):
    """Represents the decision answer made on an event request"""

    APPROVED: str = 'approved'
    APPROVED_CONDITIONALLY: str = 'approved_conditionally'
    DENIED: str = 'denied'
    DENIED_CONDITIONALLY: str = 'denied_conditionally'
