"""Tests for cynthus.messaging.common.signal.audit_identity_user_base."""

from cynthus.messaging.common.signal.audit_identity_base import AuditIdentitySignalBase
from cynthus.messaging.common.signal.audit_identity_user_base import AuditIdentityUserSignalBase


def test_user_base_sets_the_aggregate():
    assert AuditIdentityUserSignalBase.aggregate == 'user'
    assert issubclass(AuditIdentityUserSignalBase, AuditIdentitySignalBase)
