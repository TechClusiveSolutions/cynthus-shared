"""Tests for cynthus.messaging.common.signal.audit_identity_user_rejected."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_user_base import AuditIdentityUserSignalBase
from cynthus.messaging.common.signal.audit_identity_user_rejected import AuditIdentityUserRejectedSignal
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityUserRejectedSignal.name == 'audit.identity.user.rejected'


def test_components():
    assert AuditIdentityUserRejectedSignal.visibility == 'audit'
    assert AuditIdentityUserRejectedSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityUserRejectedSignal.aggregate == 'user'
    assert AuditIdentityUserRejectedSignal.action is SignalActionType.REJECTED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityUserRejectedSignal, AuditIdentityUserSignalBase)
    assert issubclass(AuditIdentityUserRejectedSignal, SignalBase)
