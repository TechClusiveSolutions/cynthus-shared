"""External Account user model class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExternalAccount(BaseModel):
    """
        Links a user to an account at an identity provider

        A user created directly has no external accounts. A user created through the Auth0 integration has one for each
        provider that signed them in (for example Google), identified by the provider's subject.
    """

    provider: str = Field(description='The identity provider, for example google-oauth2')
    subject: str = Field(description="The provider's identifier for the account")
