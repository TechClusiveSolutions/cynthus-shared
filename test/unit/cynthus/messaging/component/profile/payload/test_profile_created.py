"""Tests for cynthus.messaging.component.profile.payload.profile_created."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.profile.payload.profile_created import ProfileCreatedPayload


def test_required_fields_are_kept():
    payload = ProfileCreatedPayload(profile_id='x', user_id='x')

    assert payload.schema_version == 1
    assert payload.profile_id == 'x'
    assert payload.user_id == 'x'


def test_defaults():
    payload = ProfileCreatedPayload(profile_id='x', user_id='x')

    assert payload.changed == []


def test_profile_id_is_required():
    with pytest.raises(ValidationError):
        ProfileCreatedPayload()
