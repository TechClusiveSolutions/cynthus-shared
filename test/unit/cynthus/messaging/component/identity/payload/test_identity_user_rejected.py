"""Tests for cynthus.messaging.component.identity.payload.identity_user_rejected."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.identity.payload.identity_user_rejected import IdentityUserRejectedPayload


def test_required_fields_are_kept():
    payload = IdentityUserRejectedPayload(username='x')

    assert payload.schema_version == 1
    assert payload.username == 'x'


def test_defaults():
    payload = IdentityUserRejectedPayload(username='x')

    assert payload.reason == 'invalid_credentials'


def test_username_is_required():
    with pytest.raises(ValidationError):
        IdentityUserRejectedPayload()
