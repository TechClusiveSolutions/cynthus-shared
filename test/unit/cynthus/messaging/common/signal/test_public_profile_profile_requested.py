"""Tests for cynthus.messaging.common.signal.public_profile_profile_requested."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_profile_profile_base import PublicProfileProfileSignalBase
from cynthus.messaging.common.signal.public_profile_profile_requested import PublicProfileProfileRequestedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicProfileProfileRequestedSignal.name == 'public.profile.profile.requested'


def test_components():
    assert PublicProfileProfileRequestedSignal.visibility == 'public'
    assert PublicProfileProfileRequestedSignal.domain is SignalDomainType.PROFILE
    assert PublicProfileProfileRequestedSignal.aggregate == 'profile'
    assert PublicProfileProfileRequestedSignal.action is SignalActionType.REQUESTED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicProfileProfileRequestedSignal, PublicProfileProfileSignalBase)
    assert issubclass(PublicProfileProfileRequestedSignal, SignalBase)
