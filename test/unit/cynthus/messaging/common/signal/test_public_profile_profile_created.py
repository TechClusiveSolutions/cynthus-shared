"""Tests for cynthus.messaging.common.signal.public_profile_profile_created."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_profile_profile_base import PublicProfileProfileSignalBase
from cynthus.messaging.common.signal.public_profile_profile_created import PublicProfileProfileCreatedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicProfileProfileCreatedSignal.name == 'public.profile.profile.created'


def test_components():
    assert PublicProfileProfileCreatedSignal.visibility == 'public'
    assert PublicProfileProfileCreatedSignal.domain is SignalDomainType.PROFILE
    assert PublicProfileProfileCreatedSignal.aggregate == 'profile'
    assert PublicProfileProfileCreatedSignal.action is SignalActionType.CREATED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicProfileProfileCreatedSignal, PublicProfileProfileSignalBase)
    assert issubclass(PublicProfileProfileCreatedSignal, SignalBase)
