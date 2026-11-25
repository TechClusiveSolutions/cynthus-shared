"""Fixture factory for PartnerServiceListRespondedMessage"""

import factory

from .....common.signal import LifecycleAction, PublicPartnerServiceListRespondedSignal, SignalPayload
from .....component.partner.message import PartnerServiceListRespondedMessage
from ...base_message_factory import BaseMessageFactory
from .service_list_responded_payload import PartnerServiceListRespondedPayloadFactory


class PartnerServiceListRespondedMessageFactory(BaseMessageFactory):
    class Meta:
        model = PartnerServiceListRespondedMessage

    event_type: str = PublicPartnerServiceListRespondedSignal.name
    lifecycle_action: str = LifecycleAction.CREATED
    payload: SignalPayload = factory.SubFactory(PartnerServiceListRespondedPayloadFactory)
