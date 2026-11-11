"""Tests for cynthus.messaging.common.signal.public_profile_profile_deleted."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_profile_profile_base import PublicProfileProfileSignalBase
from cynthus.messaging.common.signal.public_profile_profile_deleted import PublicProfileProfileDeletedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicProfileProfileDeletedSignal.name == 'public.profile.profile.deleted'


def test_components():
    assert PublicProfileProfileDeletedSignal.visibility == 'public'
    assert PublicProfileProfileDeletedSignal.domain is SignalDomainType.PROFILE
    assert PublicProfileProfileDeletedSignal.aggregate == 'profile'
    assert PublicProfileProfileDeletedSignal.action is SignalActionType.DELETED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicProfileProfileDeletedSignal, PublicProfileProfileSignalBase)
    assert issubclass(PublicProfileProfileDeletedSignal, SignalBase)
