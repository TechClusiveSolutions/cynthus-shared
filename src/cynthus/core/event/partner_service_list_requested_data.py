"""Partner Service List Requested Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .partner_service_list_filters_data import PartnerServiceListFiltersData


class PartnerServiceListRequestedData(BaseModel):
    """The data of a partner service list requested event"""

    model_config = ConfigDict(extra='forbid')

    schema_version: int = Field(1, ge=1)
    filters: PartnerServiceListFiltersData = Field(default_factory=PartnerServiceListFiltersData)
