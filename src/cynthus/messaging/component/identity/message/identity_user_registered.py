"""Identity User Registered signal message for the Cynthus project"""

from ....common import AuditIdentityUserRegisteredSignal, SignalMessage
from ..payload import IdentityUserRegisteredPayload


class IdentityUserRegisteredMessage(SignalMessage[IdentityUserRegisteredPayload]):
    """
        Represents an identity user registered signal message

        Emitted by: `cynthus-auth` when a person creates an account. The account cannot sign in until the address is
        verified.
        Functional Purpose: Records the registration for `cynthus-audit`, and lets other services prepare for a new user.
    """

    event_type: str = AuditIdentityUserRegisteredSignal.name
