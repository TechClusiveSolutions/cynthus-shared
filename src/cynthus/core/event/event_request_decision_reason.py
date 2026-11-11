"""Event Request Decision Reason class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class EventRequestDecisionReason(str, Enum):
    """Represents the reason for a decision made on an event request"""

    PERMITTED: str = 'permitted'
    AUTHORIZATION_GRANTED: str = 'authorization_granted'
    AUTHORIZATION_REJECTED: str = 'authorization_rejected'
    INSUFFICIENT_PRIVILEGES: str = 'insufficient_privileges'
