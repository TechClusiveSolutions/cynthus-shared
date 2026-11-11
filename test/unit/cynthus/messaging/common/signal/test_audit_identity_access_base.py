"""Tests for cynthus.messaging.common.signal.audit_identity_access_base."""

from cynthus.messaging.common.signal.audit_identity_access_base import AuditIdentityAccessSignalBase
from cynthus.messaging.common.signal.audit_identity_base import AuditIdentitySignalBase


def test_access_base_sets_the_aggregate():
    assert AuditIdentityAccessSignalBase.aggregate == 'access'
    assert issubclass(AuditIdentityAccessSignalBase, AuditIdentitySignalBase)
