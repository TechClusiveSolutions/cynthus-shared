"""Identity Email Verified signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class IdentityEmailVerifiedPayload(SignalPayload):
    """Represents the payload part of an audit.identity.email.verified signal message. It never carries a password, a
    password hash or a token.
    """

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    user_id: str = Field(..., description='The identifier of the user whose address was verified')
    username: str = Field(..., description='The email address that was verified')
