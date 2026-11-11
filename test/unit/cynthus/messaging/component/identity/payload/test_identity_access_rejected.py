"""Tests for cynthus.messaging.component.identity.payload.identity_access_rejected."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.identity.payload.identity_access_rejected import IdentityAccessRejectedPayload


def test_required_fields_are_kept():
    payload = IdentityAccessRejectedPayload(reason='x', resource='x', method='x')

    assert payload.schema_version == 1
    assert payload.reason == 'x'
    assert payload.resource == 'x'
    assert payload.method == 'x'


def test_reason_is_required():
    with pytest.raises(ValidationError):
        IdentityAccessRejectedPayload()
