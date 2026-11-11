"""Tests for cynthus.messaging.common.signal.audit_profile_base."""

from cynthus.messaging.common.signal.audit_profile_base import AuditProfileSignalBase
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_audit_profile_signals_are_in_the_profile_domain():
    assert AuditProfileSignalBase.visibility == 'audit'
    assert AuditProfileSignalBase.domain is SignalDomainType.PROFILE
    assert issubclass(AuditProfileSignalBase, SignalBase)
