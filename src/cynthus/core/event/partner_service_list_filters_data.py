"""Partner Service List Filters Data class for the Cynthus project"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PartnerServiceListFiltersData(BaseModel):
    """The filters of a partner service list request"""

    model_config = ConfigDict(extra='forbid')

    name: str | None = None
