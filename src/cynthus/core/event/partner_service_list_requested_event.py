"""Partner Service List Requested Event class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from .partner_event import PartnerEvent
from .partner_service_list_requested_data import PartnerServiceListRequestedData


class PartnerServiceListRequestedEvent(PartnerEvent):
    """Represents a request for the list of services offered by partners"""

    data_model: ClassVar[type[BaseModel] | None] = PartnerServiceListRequestedData
