"""Tests for cynthus.messaging.common.signal.audit_profile_hard_constraint_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_profile_hard_constraint_base import AuditProfileHardConstraintSignalBase
from cynthus.messaging.common.signal.audit_profile_hard_constraint_updated import (
    AuditProfileHardConstraintUpdatedSignal,
)
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditProfileHardConstraintUpdatedSignal.name == 'audit.profile.hard_constraint.updated'


def test_components():
    assert AuditProfileHardConstraintUpdatedSignal.visibility == 'audit'
    assert AuditProfileHardConstraintUpdatedSignal.domain is SignalDomainType.PROFILE
    assert AuditProfileHardConstraintUpdatedSignal.aggregate == 'hard_constraint'
    assert AuditProfileHardConstraintUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditProfileHardConstraintUpdatedSignal, AuditProfileHardConstraintSignalBase)
    assert issubclass(AuditProfileHardConstraintUpdatedSignal, SignalBase)
