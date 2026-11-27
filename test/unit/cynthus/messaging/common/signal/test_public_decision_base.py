"""Tests for cynthus.messaging.common.signal.public_decision_base."""

import pytest

from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_decision_base import PublicDecisionSignalBase


def test_decision_domain_value():
    assert SignalDomainType.DECISION.value == 'decision'


def test_decision_base_sets_the_domain():
    assert PublicDecisionSignalBase.domain is SignalDomainType.DECISION
    assert issubclass(PublicDecisionSignalBase, SignalBase)


def test_a_concrete_subclass_without_an_aggregate_and_action_is_rejected():
    with pytest.raises(TypeError):

        class Incomplete(PublicDecisionSignalBase):
            pass
