"""Partner Service List item model for the Cynthus project"""

from uuid import UUID

from pydantic import BaseModel, Field


class PartnerServiceListItem(BaseModel):
    """One partner service in the list a caller asked for"""

    id: UUID = Field(..., description='The identifier of the service')
    name: str = Field(..., description='The name of the service')
