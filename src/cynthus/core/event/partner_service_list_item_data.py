"""Partner Service List Item Data class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PartnerServiceListItemData(BaseModel):
    """One service in the answer to a partner service list request"""

    model_config = ConfigDict(extra='forbid')

    id: UUID
    name: str
