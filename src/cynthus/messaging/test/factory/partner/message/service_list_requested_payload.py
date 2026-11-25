"""Fixture factory for PartnerServiceListRequestedPayload"""

from .....component.partner.payload import PartnerServiceListRequestedPayload
from ...base_payload_factory import BasePayloadFactory


class PartnerServiceListRequestedPayloadFactory(BasePayloadFactory):
    class Meta:
        model = PartnerServiceListRequestedPayload

