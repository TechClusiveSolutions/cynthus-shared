"""Tests for cynthus.messaging.component.identity.payload.identity_access_denied."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.identity.payload.identity_access_denied import IdentityAccessDeniedPayload


def test_required_fields_are_kept():
    payload = IdentityAccessDeniedPayload(user_id='x', required_permission='x', resource='x', method='x')

    assert payload.schema_version == 1
    assert payload.user_id == 'x'
    assert payload.required_permission == 'x'
    assert payload.resource == 'x'
    assert payload.method == 'x'


def test_defaults():
    payload = IdentityAccessDeniedPayload(user_id='x', required_permission='x', resource='x', method='x')

    assert payload.token_id is None
    assert payload.granted_permissions == []
    assert payload.roles == []


def test_user_id_is_required():
    with pytest.raises(ValidationError):
        IdentityAccessDeniedPayload()
