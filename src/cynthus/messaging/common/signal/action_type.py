"""Signal Action Type class for the Cynthus project"""

from enum import Enum


class SignalActionType(str, Enum):
    """Standardized signal action mutations"""

    ACCEPTED: str = 'accepted'
    ADDED: str = 'added'
    ASSOCIATED: str = 'associated'
    AUTHENTICATED: str = 'authenticated'
    AUTO_RESOLVED: str = 'auto_resolved'
    CAST: str = 'cast'
    CHECKED_OFF: str = 'checked_off'
    COMPUTED: str = 'computed'
    CREATED: str = 'created'
    DELETED: str = 'deleted'
    DENIED: str = 'denied'
    GENERATED: str = 'generated'
    GRANTED: str = 'granted'
    INITIATED: str = 'initiated'
    ISSUED: str = 'issued'
    MESSAGE_GENERATED: str = 'message_generated'
    MESSAGE_REQUESTED: str = 'message_requested'
    PUBLISHED: str = 'published'
    REGISTERED: str = 'registered'
    REJECTED: str = 'rejected'
    REMOVED: str = 'removed'
    REQUESTED: str = 'requested'
    RESOLVED: str = 'resolved'
    RESPONDED: str = 'responded'
    SESSION_ENDED: str = 'session_ended'
    SESSION_STARTED: str = 'session_started'
    UPDATED: str = 'updated'
    VERIFIED: str = 'verified'
