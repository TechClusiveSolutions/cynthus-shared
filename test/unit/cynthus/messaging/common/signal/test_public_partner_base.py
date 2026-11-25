"""Tests for cynthus.messaging.common.signal.public_partner_base."""

import pytest

from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_partner_base import PublicPartnerSignalBase


def test_partner_domain_value():
    assert SignalDomainType.PARTNER.value == 'partner'


def test_partner_base_sets_the_domain():
    assert PublicPartnerSignalBase.domain is SignalDomainType.PARTNER
    assert issubclass(PublicPartnerSignalBase, SignalBase)


def test_a_concrete_subclass_without_an_aggregate_and_action_is_rejected():
    with pytest.raises(TypeError):

        class Incomplete(PublicPartnerSignalBase):
            pass
