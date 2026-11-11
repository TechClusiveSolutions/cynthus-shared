"""Tests for cynthus.messaging.common.signal.audit_identity_access_granted."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.audit_identity_access_base import AuditIdentityAccessSignalBase
from cynthus.messaging.common.signal.audit_identity_access_granted import AuditIdentityAccessGrantedSignal
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType


def test_name_is_the_dotted_signal_name():
    assert AuditIdentityAccessGrantedSignal.name == 'audit.identity.access.granted'


def test_components():
    assert AuditIdentityAccessGrantedSignal.visibility == 'audit'
    assert AuditIdentityAccessGrantedSignal.domain is SignalDomainType.IDENTITY
    assert AuditIdentityAccessGrantedSignal.aggregate == 'access'
    assert AuditIdentityAccessGrantedSignal.action is SignalActionType.GRANTED


def test_derives_from_its_aggregate_base():
    assert issubclass(AuditIdentityAccessGrantedSignal, AuditIdentityAccessSignalBase)
    assert issubclass(AuditIdentityAccessGrantedSignal, SignalBase)
