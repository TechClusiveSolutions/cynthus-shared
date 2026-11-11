"""Tests for cynthus.messaging.common.signal.public_profile_base."""

from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_profile_base import PublicProfileSignalBase


def test_public_profile_signals_are_in_the_profile_domain():
    assert PublicProfileSignalBase.visibility == 'public'
    assert PublicProfileSignalBase.domain is SignalDomainType.PROFILE
    assert issubclass(PublicProfileSignalBase, SignalBase)
