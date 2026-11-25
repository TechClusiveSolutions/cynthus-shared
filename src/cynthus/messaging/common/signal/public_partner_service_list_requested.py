"""Public Partner Service List Requested signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_partner_service_list_base import PublicPartnerServiceListSignalBase


class PublicPartnerServiceListRequestedSignal(PublicPartnerServiceListSignalBase):
    """Concrete signal: public.partner.service_list.requested"""

    action = SignalActionType.REQUESTED
