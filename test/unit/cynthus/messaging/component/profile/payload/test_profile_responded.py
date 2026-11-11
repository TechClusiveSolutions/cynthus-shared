"""Tests for cynthus.messaging.component.profile.payload.profile_responded."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.profile.payload.profile_responded import ProfileRespondedPayload


def test_required_fields_are_kept():
    payload = ProfileRespondedPayload(operation='x', status=1)

    assert payload.schema_version == 1
    assert payload.operation == 'x'
    assert payload.status == 1


def test_defaults():
    payload = ProfileRespondedPayload(operation='x', status=1)

    assert payload.result is None
    assert payload.error is None


def test_operation_is_required():
    with pytest.raises(ValidationError):
        ProfileRespondedPayload()
