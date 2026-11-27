"""Tests for cynthus.messaging.common.signal.public_decision_event_request_denied_conditionally."""

from cynthus.messaging import common
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_decision_event_request_base import PublicDecisionEventRequestSignalBase
from cynthus.messaging.common.signal.public_decision_event_request_denied_conditionally import (
    PublicDecisionEventRequestDeniedConditionallySignal,
)


def test_name_is_the_dotted_signal_name():
    assert PublicDecisionEventRequestDeniedConditionallySignal.name == 'public.decision.event_request.denied_conditionally'


def test_components():
    assert PublicDecisionEventRequestDeniedConditionallySignal.visibility == 'public'
    assert PublicDecisionEventRequestDeniedConditionallySignal.domain is SignalDomainType.DECISION
    assert PublicDecisionEventRequestDeniedConditionallySignal.aggregate == 'event_request'
    assert PublicDecisionEventRequestDeniedConditionallySignal.action is SignalActionType.DENIED_CONDITIONALLY


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicDecisionEventRequestDeniedConditionallySignal, PublicDecisionEventRequestSignalBase)
    assert issubclass(PublicDecisionEventRequestDeniedConditionallySignal, SignalBase)


def test_is_exported_from_the_common_package():
    assert common.PublicDecisionEventRequestDeniedConditionallySignal is PublicDecisionEventRequestDeniedConditionallySignal
