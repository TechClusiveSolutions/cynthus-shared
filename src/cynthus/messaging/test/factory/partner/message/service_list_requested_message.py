"""Fixture factory for PartnerServiceListRequestedMessage"""

import factory

from .....common.signal import LifecycleAction, PublicPartnerServiceListRequestedSignal, SignalPayload
from .....component.partner.message import PartnerServiceListRequestedMessage
from ...base_message_factory import BaseMessageFactory
from .service_list_requested_payload import PartnerServiceListRequestedPayloadFactory


class PartnerServiceListRequestedMessageFactory(BaseMessageFactory):
    class Meta:
        model = PartnerServiceListRequestedMessage

    event_type: str = PublicPartnerServiceListRequestedSignal.name
    lifecycle_action: str = LifecycleAction.CREATED
    payload: SignalPayload = factory.SubFactory(PartnerServiceListRequestedPayloadFactory)
