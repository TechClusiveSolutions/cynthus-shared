"""Tests for cynthus.messaging.common.signal.public_decision_event_request_approved."""

from cynthus.messaging import common
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_decision_event_request_approved import (
    PublicDecisionEventRequestApprovedSignal,
)
from cynthus.messaging.common.signal.public_decision_event_request_base import PublicDecisionEventRequestSignalBase


def test_name_is_the_dotted_signal_name():
    assert PublicDecisionEventRequestApprovedSignal.name == 'public.decision.event_request.approved'


def test_components():
    assert PublicDecisionEventRequestApprovedSignal.visibility == 'public'
    assert PublicDecisionEventRequestApprovedSignal.domain is SignalDomainType.DECISION
    assert PublicDecisionEventRequestApprovedSignal.aggregate == 'event_request'
    assert PublicDecisionEventRequestApprovedSignal.action is SignalActionType.APPROVED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicDecisionEventRequestApprovedSignal, PublicDecisionEventRequestSignalBase)
    assert issubclass(PublicDecisionEventRequestApprovedSignal, SignalBase)


def test_is_exported_from_the_common_package():
    assert common.PublicDecisionEventRequestApprovedSignal is PublicDecisionEventRequestApprovedSignal
