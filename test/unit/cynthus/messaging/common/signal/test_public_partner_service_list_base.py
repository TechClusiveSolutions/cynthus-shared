"""Tests for cynthus.messaging.common.signal.public_partner_service_list_base."""

import pytest

from cynthus.messaging.common.signal.public_partner_base import PublicPartnerSignalBase
from cynthus.messaging.common.signal.public_partner_service_list_base import PublicPartnerServiceListSignalBase


def test_service_list_base_sets_the_aggregate():
    assert PublicPartnerServiceListSignalBase.aggregate == 'service_list'
    assert issubclass(PublicPartnerServiceListSignalBase, PublicPartnerSignalBase)


def test_a_concrete_subclass_without_an_action_is_rejected():
    with pytest.raises(TypeError):

        class Incomplete(PublicPartnerServiceListSignalBase):
            pass
