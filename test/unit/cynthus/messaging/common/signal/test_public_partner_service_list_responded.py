"""Tests for cynthus.messaging.common.signal.public_partner_service_list_responded."""

from cynthus.messaging import common
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_partner_service_list_base import PublicPartnerServiceListSignalBase
from cynthus.messaging.common.signal.public_partner_service_list_responded import (
    PublicPartnerServiceListRespondedSignal,
)


def test_name_is_the_dotted_signal_name():
    assert PublicPartnerServiceListRespondedSignal.name == 'public.partner.service_list.responded'


def test_components():
    assert PublicPartnerServiceListRespondedSignal.visibility == 'public'
    assert PublicPartnerServiceListRespondedSignal.domain is SignalDomainType.PARTNER
    assert PublicPartnerServiceListRespondedSignal.aggregate == 'service_list'
    assert PublicPartnerServiceListRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicPartnerServiceListRespondedSignal, PublicPartnerServiceListSignalBase)
    assert issubclass(PublicPartnerServiceListRespondedSignal, SignalBase)


def test_is_exported_from_the_common_package():
    assert common.PublicPartnerServiceListRespondedSignal is PublicPartnerServiceListRespondedSignal
