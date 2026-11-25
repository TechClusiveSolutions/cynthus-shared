"""Tests for cynthus.messaging.common.signal.public_partner_service_list_requested."""

from cynthus.messaging import common
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_partner_service_list_base import PublicPartnerServiceListSignalBase
from cynthus.messaging.common.signal.public_partner_service_list_requested import (
    PublicPartnerServiceListRequestedSignal,
)


def test_name_is_the_dotted_signal_name():
    assert PublicPartnerServiceListRequestedSignal.name == 'public.partner.service_list.requested'


def test_components():
    assert PublicPartnerServiceListRequestedSignal.visibility == 'public'
    assert PublicPartnerServiceListRequestedSignal.domain is SignalDomainType.PARTNER
    assert PublicPartnerServiceListRequestedSignal.aggregate == 'service_list'
    assert PublicPartnerServiceListRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicPartnerServiceListRequestedSignal, PublicPartnerServiceListSignalBase)
    assert issubclass(PublicPartnerServiceListRequestedSignal, SignalBase)


def test_is_exported_from_the_common_package():
    assert common.PublicPartnerServiceListRequestedSignal is PublicPartnerServiceListRequestedSignal
