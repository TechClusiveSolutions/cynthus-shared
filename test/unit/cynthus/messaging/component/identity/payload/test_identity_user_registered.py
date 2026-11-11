"""Tests for cynthus.messaging.component.identity.payload.identity_user_registered."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.common import SignalPayload
from cynthus.messaging.component.identity.payload.identity_user_registered import IdentityUserRegisteredPayload


def test_required_fields_are_kept():
    payload = IdentityUserRegisteredPayload(user_id='u1', username='ada@example.com')

    assert payload.schema_version == 1
    assert payload.user_id == 'u1'
    assert payload.username == 'ada@example.com'


@pytest.mark.parametrize('fields', [{}, {'user_id': 'u1'}, {'username': 'ada@example.com'}])
def test_both_fields_are_required(fields):
    with pytest.raises(ValidationError):
        IdentityUserRegisteredPayload(**fields)


def test_it_carries_no_secret():
    own = set(IdentityUserRegisteredPayload.model_fields) - set(SignalPayload.model_fields)

    assert own == {'user_id', 'username'}
    assert not any(
        word in name for name in IdentityUserRegisteredPayload.model_fields for word in ('password', 'hash', 'token')
    )


def test_a_secret_passed_anyway_is_not_kept():
    payload = IdentityUserRegisteredPayload(user_id='u1', username='a@b.co', password='hunter2')

    assert 'hunter2' not in payload.model_dump_json()
