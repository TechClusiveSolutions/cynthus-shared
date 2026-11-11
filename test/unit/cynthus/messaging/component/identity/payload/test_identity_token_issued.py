"""Tests for cynthus.messaging.component.identity.payload.identity_token_issued."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.identity.payload.identity_token_issued import IdentityTokenIssuedPayload


def test_required_fields_are_kept():
    payload = IdentityTokenIssuedPayload(user_id='x', token_id='x', key_id='x', expires_in=1)

    assert payload.schema_version == 1
    assert payload.user_id == 'x'
    assert payload.token_id == 'x'
    assert payload.key_id == 'x'
    assert payload.expires_in == 1


def test_defaults():
    payload = IdentityTokenIssuedPayload(user_id='x', token_id='x', key_id='x', expires_in=1)

    assert payload.roles == []
    assert payload.permissions == []


def test_user_id_is_required():
    with pytest.raises(ValidationError):
        IdentityTokenIssuedPayload()
