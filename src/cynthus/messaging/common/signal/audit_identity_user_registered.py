"""Audit Identity User Registered signal class for the Cynthus project"""

from .action_type import SignalActionType
from .audit_identity_user_base import AuditIdentityUserSignalBase


class AuditIdentityUserRegisteredSignal(AuditIdentityUserSignalBase):
    """Concrete signal: audit.identity.user.registered"""

    action = SignalActionType.REGISTERED
