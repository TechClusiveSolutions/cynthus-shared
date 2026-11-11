"""Tests for cynthus.messaging.common.signal.audit_identity_token_base."""

from cynthus.messaging.common.signal.audit_identity_base import AuditIdentitySignalBase
from cynthus.messaging.common.signal.audit_identity_token_base import AuditIdentityTokenSignalBase


def test_token_base_sets_the_aggregate():
    assert AuditIdentityTokenSignalBase.aggregate == 'token'
    assert issubclass(AuditIdentityTokenSignalBase, AuditIdentitySignalBase)
