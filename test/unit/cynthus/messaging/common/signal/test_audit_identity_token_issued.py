"""Tests for cynthus.messaging.common.signal.audit_identity_token_issued."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_token_base import AuditIdentityTokenSignalBase
from cynthus.messaging.common.signal.audit_identity_token_issued import AuditIdentityTokenIssuedSignal
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityTokenIssuedSignal.name == 'audit.identity.token.issued'


def test_components():
    assert AuditIdentityTokenIssuedSignal.visibility == 'audit'
    assert AuditIdentityTokenIssuedSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityTokenIssuedSignal.aggregate == 'token'
    assert AuditIdentityTokenIssuedSignal.action is SignalActionType.ISSUED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityTokenIssuedSignal, AuditIdentityTokenSignalBase)
    assert issubclass(AuditIdentityTokenIssuedSignal, SignalBase)
