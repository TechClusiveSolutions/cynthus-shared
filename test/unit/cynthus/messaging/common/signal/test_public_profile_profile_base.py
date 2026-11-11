"""Tests for cynthus.messaging.common.signal.public_profile_profile_base."""

from cynthus.messaging.common.signal.public_profile_base import PublicProfileSignalBase
from cynthus.messaging.common.signal.public_profile_profile_base import PublicProfileProfileSignalBase


def test_profile_base_sets_the_aggregate():
    assert PublicProfileProfileSignalBase.aggregate == 'profile'
    assert issubclass(PublicProfileProfileSignalBase, PublicProfileSignalBase)
