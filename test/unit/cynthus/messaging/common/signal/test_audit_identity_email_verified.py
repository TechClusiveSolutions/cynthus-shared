"""Tests for cynthus.messaging.common.signal.audit_identity_email_verified."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_email_base import AuditIdentityEmailSignalBase
from cynthus.messaging.common.signal.audit_identity_email_verified import AuditIdentityEmailVerifiedSignal
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityEmailVerifiedSignal.name == 'audit.identity.email.verified'


def test_components():
    assert AuditIdentityEmailVerifiedSignal.visibility == 'audit'
    assert AuditIdentityEmailVerifiedSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityEmailVerifiedSignal.aggregate == 'email'
    assert AuditIdentityEmailVerifiedSignal.action is SignalActionType.VERIFIED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityEmailVerifiedSignal, AuditIdentityEmailSignalBase)
    assert issubclass(AuditIdentityEmailVerifiedSignal, SignalBase)
