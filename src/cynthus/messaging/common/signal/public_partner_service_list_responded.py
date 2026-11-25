"""Public Partner Service List Responded signal class for the Cynthus project"""

from .action_type import SignalActionType
from .public_partner_service_list_base import PublicPartnerServiceListSignalBase


class PublicPartnerServiceListRespondedSignal(PublicPartnerServiceListSignalBase):
    """Concrete signal: public.partner.service_list.responded"""

    action = SignalActionType.RESPONDED
