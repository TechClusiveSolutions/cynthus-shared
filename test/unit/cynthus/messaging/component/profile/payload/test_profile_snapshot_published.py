"""Tests for cynthus.messaging.component.profile.payload.profile_snapshot_published."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.profile.payload.profile_snapshot_published import ProfileSnapshotPublishedPayload


def test_required_fields_are_kept():
    payload = ProfileSnapshotPublishedPayload(user_id='x', profile={'a': 1})

    assert payload.schema_version == 1
    assert payload.user_id == 'x'
    assert payload.profile == {'a': 1}


def test_defaults():
    payload = ProfileSnapshotPublishedPayload(user_id='x', profile={'a': 1})

    assert payload.reason == 'authentication'


def test_user_id_is_required():
    with pytest.raises(ValidationError):
        ProfileSnapshotPublishedPayload()
