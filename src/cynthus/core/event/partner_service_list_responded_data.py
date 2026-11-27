"""Partner Service List Responded Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .partner_service_list_item_data import PartnerServiceListItemData


class PartnerServiceListRespondedData(BaseModel):
    """The data of a partner service list responded event"""

    model_config = ConfigDict(extra='forbid')

    schema_version: int = Field(1, ge=1)
    status: int
    result: list[PartnerServiceListItemData] | None = None
    error: str | None = None
