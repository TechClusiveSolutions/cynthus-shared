"""Fixture factory for PartnerServiceListRespondedPayload"""

from .....component.partner.payload import PartnerServiceListRespondedPayload
from ...base_payload_factory import BasePayloadFactory


class PartnerServiceListRespondedPayloadFactory(BasePayloadFactory):
    class Meta:
        model = PartnerServiceListRespondedPayload

    status: int = 200
