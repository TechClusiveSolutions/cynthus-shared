"""Identity Email Verified signal message for the Cynthus project"""

from ....common import AuditIdentityEmailVerifiedSignal, SignalMessage
from ..payload import IdentityEmailVerifiedPayload


class IdentityEmailVerifiedMessage(SignalMessage[IdentityEmailVerifiedPayload]):
    """
        Represents an identity email verified signal message

        Emitted by: `cynthus-auth` when a person uses the link in the verification email.
        Functional Purpose: Records that the account can now sign in, for `cynthus-audit`, and lets other services react to
        a user who is ready to use the application.
    """

    event_type: str = AuditIdentityEmailVerifiedSignal.name
