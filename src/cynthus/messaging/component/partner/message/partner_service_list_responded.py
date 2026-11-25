"""Partner Service List Responded signal message for the Cynthus project"""

from ....common import PublicPartnerServiceListRespondedSignal, SignalMessage
from ..payload import PartnerServiceListRespondedPayload


class PartnerServiceListRespondedMessage(SignalMessage[PartnerServiceListRespondedPayload]):
    """
        Represents a partner service list responded signal message

        Emitted by: `cynthus-partner-api` when it has dealt with a request for the partner service list.
        Functional Purpose: Carries the outcome back to `cynthus-core-api`, which relays it to the caller.
    """

    event_type: str = PublicPartnerServiceListRespondedSignal.name
