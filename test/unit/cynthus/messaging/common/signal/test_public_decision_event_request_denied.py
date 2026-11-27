"""Tests for cynthus.messaging.common.signal.public_decision_event_request_denied."""

from cynthus.messaging import common
from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_decision_event_request_base import PublicDecisionEventRequestSignalBase
from cynthus.messaging.common.signal.public_decision_event_request_denied import (
    PublicDecisionEventRequestDeniedSignal,
)


def test_name_is_the_dotted_signal_name():
    assert PublicDecisionEventRequestDeniedSignal.name == 'public.decision.event_request.denied'


def test_components():
    assert PublicDecisionEventRequestDeniedSignal.visibility == 'public'
    assert PublicDecisionEventRequestDeniedSignal.domain is SignalDomainType.DECISION
    assert PublicDecisionEventRequestDeniedSignal.aggregate == 'event_request'
    assert PublicDecisionEventRequestDeniedSignal.action is SignalActionType.DENIED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicDecisionEventRequestDeniedSignal, PublicDecisionEventRequestSignalBase)
    assert issubclass(PublicDecisionEventRequestDeniedSignal, SignalBase)


def test_is_exported_from_the_common_package():
    assert common.PublicDecisionEventRequestDeniedSignal is PublicDecisionEventRequestDeniedSignal
