"""Tests for cynthus.messaging.common.signal.audit_identity_access_denied."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_access_base import AuditIdentityAccessSignalBase
from cynthus.messaging.common.signal.audit_identity_access_denied import AuditIdentityAccessDeniedSignal
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityAccessDeniedSignal.name == 'audit.identity.access.denied'


def test_components():
    assert AuditIdentityAccessDeniedSignal.visibility == 'audit'
    assert AuditIdentityAccessDeniedSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityAccessDeniedSignal.aggregate == 'access'
    assert AuditIdentityAccessDeniedSignal.action is SignalActionType.DENIED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityAccessDeniedSignal, AuditIdentityAccessSignalBase)
    assert issubclass(AuditIdentityAccessDeniedSignal, SignalBase)
