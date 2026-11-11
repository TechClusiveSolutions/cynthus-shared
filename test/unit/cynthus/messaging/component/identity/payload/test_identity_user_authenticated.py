"""Tests for cynthus.messaging.component.identity.payload.identity_user_authenticated."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.identity.payload.identity_user_authenticated import IdentityUserAuthenticatedPayload


def test_required_fields_are_kept():
    payload = IdentityUserAuthenticatedPayload(user_id='x', username='x')

    assert payload.schema_version == 1
    assert payload.user_id == 'x'
    assert payload.username == 'x'


def test_defaults():
    payload = IdentityUserAuthenticatedPayload(user_id='x', username='x')

    assert payload.method == 'password'


def test_user_id_is_required():
    with pytest.raises(ValidationError):
        IdentityUserAuthenticatedPayload()
