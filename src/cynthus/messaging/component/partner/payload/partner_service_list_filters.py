"""Partner Service List filters model for the Cynthus project"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PartnerServiceListFilters(BaseModel):
    """Narrows the list of partner services a caller asks for"""

    model_config = ConfigDict(extra='forbid')

    name: Optional[str] = Field(default=None, description='Optional; case-insensitive contains. With no name, all partners are returned.')
