"""Tests for cynthus.messaging.common.signal.public_profile_profile_updated."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_profile_profile_base import PublicProfileProfileSignalBase
from cynthus.messaging.common.signal.public_profile_profile_updated import PublicProfileProfileUpdatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicProfileProfileUpdatedSignal.name == 'public.profile.profile.updated'


def test_components():
    assert PublicProfileProfileUpdatedSignal.visibility == 'public'
    assert PublicProfileProfileUpdatedSignal.domain is SignalDomainType.PROFILE
    assert PublicProfileProfileUpdatedSignal.aggregate == 'profile'
    assert PublicProfileProfileUpdatedSignal.action is SignalActionType.UPDATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicProfileProfileUpdatedSignal, PublicProfileProfileSignalBase)
    assert issubclass(PublicProfileProfileUpdatedSignal, SignalBase)
