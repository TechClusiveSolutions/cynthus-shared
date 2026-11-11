"""Tests for cynthus.messaging.common.signal.public_profile_snapshot_base."""

from cynthus.messaging.common.signal.public_profile_base import PublicProfileSignalBase
from cynthus.messaging.common.signal.public_profile_snapshot_base import PublicProfileSnapshotSignalBase


def test_snapshot_base_sets_the_aggregate():
    assert PublicProfileSnapshotSignalBase.aggregate == 'snapshot'
    assert issubclass(PublicProfileSnapshotSignalBase, PublicProfileSignalBase)
