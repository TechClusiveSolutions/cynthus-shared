"""Identity User Registered signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload


class IdentityUserRegisteredPayload(SignalPayload):
    """Represents the payload part of an audit.identity.user.registered signal message. It never carries a password, a
    password hash or a token.
    """

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    user_id: str = Field(..., description='The identifier of the new user')
    username: str = Field(..., description='The email address the account was registered with')
