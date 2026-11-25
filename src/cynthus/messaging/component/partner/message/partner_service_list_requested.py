"""Partner Service List Requested signal message for the Cynthus project"""

from ....common import PublicPartnerServiceListRequestedSignal, SignalMessage
from ..payload import PartnerServiceListRequestedPayload


class PartnerServiceListRequestedMessage(SignalMessage[PartnerServiceListRequestedPayload]):
    """
        Represents a partner service list requested signal message

        Emitted by: `cynthus-core-api` when a caller asks for the list of services offered by partners.
        Functional Purpose: Hands the request to the Partner service so the caller gets an immediate acknowledgement.
    """

    event_type: str = PublicPartnerServiceListRequestedSignal.name
