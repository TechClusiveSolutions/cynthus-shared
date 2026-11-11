"""Tests for cynthus.messaging.common.signal.audit_identity_user_authenticated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_user_authenticated import AuditIdentityUserAuthenticatedSignal
from cynthus.messaging.common.signal.audit_identity_user_base import AuditIdentityUserSignalBase
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityUserAuthenticatedSignal.name == 'audit.identity.user.authenticated'


def test_components():
    assert AuditIdentityUserAuthenticatedSignal.visibility == 'audit'
    assert AuditIdentityUserAuthenticatedSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityUserAuthenticatedSignal.aggregate == 'user'
    assert AuditIdentityUserAuthenticatedSignal.action is SignalActionType.AUTHENTICATED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityUserAuthenticatedSignal, AuditIdentityUserSignalBase)
    assert issubclass(AuditIdentityUserAuthenticatedSignal, SignalBase)
