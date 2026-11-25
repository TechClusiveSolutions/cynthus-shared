"""Public Partner Service List Signal Base class for the Cynthus project"""

from .public_partner_base import PublicPartnerSignalBase


class PublicPartnerServiceListSignalBase(PublicPartnerSignalBase, abstract=True):
    """Intermediate base for all public partner service list signals. Sets the aggregate component."""

    aggregate = 'service_list'
