"""Audit Identity Email Verified signal class for the Cynthus project"""

from .action_type import SignalActionType
from .audit_identity_email_base import AuditIdentityEmailSignalBase


class AuditIdentityEmailVerifiedSignal(AuditIdentityEmailSignalBase):
    """Concrete signal: audit.identity.email.verified"""

    action = SignalActionType.VERIFIED
