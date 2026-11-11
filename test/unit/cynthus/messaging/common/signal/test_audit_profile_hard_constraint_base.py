"""Tests for cynthus.messaging.common.signal.audit_profile_hard_constraint_base."""

from cynthus.messaging.common.signal.audit_profile_base import AuditProfileSignalBase
from cynthus.messaging.common.signal.audit_profile_hard_constraint_base import AuditProfileHardConstraintSignalBase


def test_hard_constraint_base_sets_the_aggregate():
    assert AuditProfileHardConstraintSignalBase.aggregate == 'hard_constraint'
    assert issubclass(AuditProfileHardConstraintSignalBase, AuditProfileSignalBase)
