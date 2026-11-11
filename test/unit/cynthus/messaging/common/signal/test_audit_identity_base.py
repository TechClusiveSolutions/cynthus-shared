"""Tests for cynthus.messaging.common.signal.audit_identity_base."""

from cynthus.messaging.common.signal.audit_identity_base import AuditIdentitySignalBase
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_identity_signals_are_audit_signals_in_the_identity_domain():
    assert AuditIdentitySignalBase.visibility == 'audit'
    assert AuditIdentitySignalBase.domain is SignalDomainType.IDENTITY
    assert issubclass(AuditIdentitySignalBase, SignalBase)
