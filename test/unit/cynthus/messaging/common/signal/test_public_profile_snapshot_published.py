"""Tests for cynthus.messaging.common.signal.public_profile_snapshot_published."""

from cynthus.messaging.common.signal.action_type import SignalActionType
from cynthus.messaging.common.signal.base import SignalBase
from cynthus.messaging.common.signal.domain_type import SignalDomainType
from cynthus.messaging.common.signal.public_profile_snapshot_base import PublicProfileSnapshotSignalBase
from cynthus.messaging.common.signal.public_profile_snapshot_published import PublicProfileSnapshotPublishedSignal


def test_name_is_the_dotted_signal_name():
    assert PublicProfileSnapshotPublishedSignal.name == 'public.profile.snapshot.published'


def test_components():
    assert PublicProfileSnapshotPublishedSignal.visibility == 'public'
    assert PublicProfileSnapshotPublishedSignal.domain is SignalDomainType.PROFILE
    assert PublicProfileSnapshotPublishedSignal.aggregate == 'snapshot'
    assert PublicProfileSnapshotPublishedSignal.action is SignalActionType.PUBLISHED


def test_derives_from_its_aggregate_base():
    assert issubclass(PublicProfileSnapshotPublishedSignal, PublicProfileSnapshotSignalBase)
    assert issubclass(PublicProfileSnapshotPublishedSignal, SignalBase)
