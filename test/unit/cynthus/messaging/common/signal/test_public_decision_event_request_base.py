"""Tests for cynthus.messaging.common.signal.public_decision_event_request_base."""

import pytest

from cynthus.messaging.common.signal.public_decision_base import PublicDecisionSignalBase
from cynthus.messaging.common.signal.public_decision_event_request_base import PublicDecisionEventRequestSignalBase


def test_event_request_base_sets_the_aggregate():
    assert PublicDecisionEventRequestSignalBase.aggregate == 'event_request'
    assert issubclass(PublicDecisionEventRequestSignalBase, PublicDecisionSignalBase)


def test_a_concrete_subclass_without_an_action_is_rejected():
    with pytest.raises(TypeError):

        class Incomplete(PublicDecisionEventRequestSignalBase):
            pass
