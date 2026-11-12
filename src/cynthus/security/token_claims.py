"""Access token claims for the Cynthus project"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# The workspace id of a person who has not made a workspace yet (ADR-010 amendment); no data belongs to it
NO_WORKSPACE = UUID(int=0)


class TokenClaims(BaseModel):
    """What a verified access token says about its holder"""

    model_config = ConfigDict(frozen=True)

    subject: UUID = Field(description='The user the token was issued to (the `sub` claim)')
    organization_id: UUID = Field(description='Deprecated alias of the tenant id (ADR-010); the same value')
    workspace_id: UUID = Field(description='The workspace the token is valid for')
    token_id: Optional[str] = Field(default=None, description='The identifier of the token (the `jti` claim)')
    roles: List[str] = Field(default_factory=list, description='Roles granted to the user')
    permissions: List[str] = Field(default_factory=list, description='Permissions such as inventory:read')
    issued_at: int = Field(description='Seconds since the epoch when the token was issued')
    expires_at: int = Field(description='Seconds since the epoch when the token stops being valid')

    @property
    def tenant_id(self) -> UUID:
        """The tenant the user belongs to (ADR-010); the value that ``organization_id`` also holds."""

        return self.organization_id

    @property
    def has_workspace(self) -> bool:
        """False for the nil workspace id: the person has not made or entered a workspace, so no data is theirs to reach."""

        return self.workspace_id != NO_WORKSPACE

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
