"""Event Request Answer Reason class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class EventRequestAnswerReason(str, Enum):
    """
        Why the answer to an event request is what it is (ADR-013)

        The same words are what a condition waits for: a condition is met when a reply carries exactly the answer reason the
        condition names. These are the reasons every service shares; a service may use others of its own (for example
        ``payment_method_linked``), because the field that holds a reason is plain text and compares equal to the member's value.
    """

    PERMITTED: str = 'permitted'
    APPROVAL_REQUIRED: str = 'approval_required'
    APPROVAL_GRANTED: str = 'approval_granted'
    APPROVAL_DENIED: str = 'approval_denied'
    INSUFFICIENT_PRIVILEGES: str = 'insufficient_privileges'
    EXPIRED: str = 'expired'
