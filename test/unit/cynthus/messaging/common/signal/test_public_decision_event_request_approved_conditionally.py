"""Tests for cynthus.messaging.common.signal.public_decision_event_request_approved_conditionally."""

from cynthus.messaging import common
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_decision_event_request_approved_conditionally import (
    PublicDecisionEventRequestApprovedConditionallySignal,
)
from cynthus.messaging.common.signal.public_decision_event_request_base import PublicDecisionEventRequestSignalBase


def test_name_is_the_dotted_signal_name():
    assert PublicDecisionEventRequestApprovedConditionallySignal.name == 'public.decision.event_request.approved_conditionally'


def test_components():
    assert PublicDecisionEventRequestApprovedConditionallySignal.visibility == 'public'
    assert PublicDecisionEventRequestApprovedConditionallySignal.domain is SignalDomainType.DECISION
    assert PublicDecisionEventRequestApprovedConditionallySignal.aggregate == 'event_request'
    assert PublicDecisionEventRequestApprovedConditionallySignal.action is SignalActionType.APPROVED_CONDITIONALLY


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicDecisionEventRequestApprovedConditionallySignal, PublicDecisionEventRequestSignalBase)
    assert issubclass(PublicDecisionEventRequestApprovedConditionallySignal, SignalBase)


def test_is_exported_from_the_common_package():
    assert common.PublicDecisionEventRequestApprovedConditionallySignal is PublicDecisionEventRequestApprovedConditionallySignal
