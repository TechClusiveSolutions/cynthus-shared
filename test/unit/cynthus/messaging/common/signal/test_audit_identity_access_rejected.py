"""Tests for cynthus.messaging.common.signal.audit_identity_access_rejected."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_access_base import AuditIdentityAccessSignalBase
from cynthus.messaging.common.signal.audit_identity_access_rejected import AuditIdentityAccessRejectedSignal
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityAccessRejectedSignal.name == 'audit.identity.access.rejected'


def test_components():
    assert AuditIdentityAccessRejectedSignal.visibility == 'audit'
    assert AuditIdentityAccessRejectedSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityAccessRejectedSignal.aggregate == 'access'
    assert AuditIdentityAccessRejectedSignal.action is SignalActionType.REJECTED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityAccessRejectedSignal, AuditIdentityAccessSignalBase)
    assert issubclass(AuditIdentityAccessRejectedSignal, SignalBase)
