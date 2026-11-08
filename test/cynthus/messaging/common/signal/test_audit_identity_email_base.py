"""Tests for cynthus.messaging.common.signal.audit_identity_email_base."""

from cynthus.messaging.common.signal.audit_identity_base import AuditIdentitySignalBase
from cynthus.messaging.common.signal.audit_identity_email_base import AuditIdentityEmailSignalBase


def test_email_base_sets_the_aggregate():
    assert AuditIdentityEmailSignalBase.aggregate == 'email'
    assert issubclass(AuditIdentityEmailSignalBase, AuditIdentitySignalBase)
