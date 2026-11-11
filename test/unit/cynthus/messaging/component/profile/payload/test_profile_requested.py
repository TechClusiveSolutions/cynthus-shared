"""Tests for cynthus.messaging.component.profile.payload.profile_requested."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.profile.payload.profile_requested import ProfileRequestedPayload


def test_required_fields_are_kept():
    payload = ProfileRequestedPayload(operation='get')

    assert payload.schema_version == 1
    assert payload.operation == 'get'


def test_defaults():
    payload = ProfileRequestedPayload(operation='get')

    assert payload.resource_id is None
    assert payload.data == {}


def test_operation_is_required():
    with pytest.raises(ValidationError):
        ProfileRequestedPayload()
