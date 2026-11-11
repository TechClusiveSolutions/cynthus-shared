"""Tests for cynthus.messaging.common.signal.audit_identity_user_registered."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_user_base import AuditIdentityUserSignalBase
from cynthus.messaging.common.signal.audit_identity_user_registered import AuditIdentityUserRegisteredSignal
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityUserRegisteredSignal.name == 'audit.identity.user.registered'


def test_components():
    assert AuditIdentityUserRegisteredSignal.visibility == 'audit'
    assert AuditIdentityUserRegisteredSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityUserRegisteredSignal.aggregate == 'user'
    assert AuditIdentityUserRegisteredSignal.action is SignalActionType.REGISTERED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityUserRegisteredSignal, AuditIdentityUserSignalBase)
    assert issubclass(AuditIdentityUserRegisteredSignal, SignalBase)
