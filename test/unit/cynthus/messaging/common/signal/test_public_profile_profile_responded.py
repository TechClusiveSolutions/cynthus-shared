"""Tests for cynthus.messaging.common.signal.public_profile_profile_responded."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_profile_profile_base import PublicProfileProfileSignalBase
from cynthus.messaging.common.signal.public_profile_profile_responded import PublicProfileProfileRespondedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicProfileProfileRespondedSignal.name == 'public.profile.profile.responded'


def test_components():
    assert PublicProfileProfileRespondedSignal.visibility == 'public'
    assert PublicProfileProfileRespondedSignal.domain is SignalDomainType.PROFILE
    assert PublicProfileProfileRespondedSignal.aggregate == 'profile'
    assert PublicProfileProfileRespondedSignal.action is SignalActionType.RESPONDED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicProfileProfileRespondedSignal, PublicProfileProfileSignalBase)
    assert issubclass(PublicProfileProfileRespondedSignal, SignalBase)
