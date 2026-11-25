"""Partner Service List Responded signal payload class for the Cynthus project"""

from typing import Optional

from pydantic import Field

from ....common import SignalPayload
from .partner_service_list_item import PartnerServiceListItem


class PartnerServiceListRespondedPayload(SignalPayload):
    """Represents the payload part of a public.partner.service_list.responded signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    status: int = Field(..., description='200 when it worked; 401, 403 or 422 when it did not')
    result: Optional[list[PartnerServiceListItem]] = Field(default=None, description='The services, when it worked')
    error: Optional[str] = Field(default=None, description='Why the request failed')
