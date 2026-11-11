"""Tests for cynthus.messaging.component.profile.payload.profile_hard_constraint_updated."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.profile.payload.profile_hard_constraint_updated import (
    ProfileHardConstraintUpdatedPayload,
)


def test_required_fields_are_kept():
    payload = ProfileHardConstraintUpdatedPayload(user_id='x', profile_id='x', kind='x')

    assert payload.schema_version == 1
    assert payload.user_id == 'x'
    assert payload.profile_id == 'x'
    assert payload.kind == 'x'


def test_defaults():
    payload = ProfileHardConstraintUpdatedPayload(user_id='x', profile_id='x', kind='x')

    assert payload.added == []
    assert payload.removed == []


def test_user_id_is_required():
    with pytest.raises(ValidationError):
        ProfileHardConstraintUpdatedPayload()
