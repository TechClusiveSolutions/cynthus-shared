"""Partner Service List Requested signal payload class for the Cynthus project"""

from pydantic import Field

from ....common import SignalPayload
from .partner_service_list_filters import PartnerServiceListFilters


class PartnerServiceListRequestedPayload(SignalPayload):
    """Represents the payload part of a public.partner.service_list.requested signal message"""

    schema_version: int = Field(default=1, ge=1, description='Version of this payload contract')
    filters: PartnerServiceListFilters = Field(
        default_factory=PartnerServiceListFilters, description='Narrows the list, for example by name'
    )
