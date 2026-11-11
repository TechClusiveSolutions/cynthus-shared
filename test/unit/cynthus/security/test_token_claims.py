import uuid

import pytest
from pydantic import ValidationError

from cynthus.security import TokenClaims


def _claims(**changes):
    values = {
        'subject': uuid.uuid4(), 'organization_id': uuid.uuid4(), 'workspace_id': uuid.uuid4(),
        'permissions': ['inventory:read'], 'issued_at': 1, 'expires_at': 2,
    }
    values.update(changes)

    return TokenClaims(**values)


def test_a_permission_is_granted_only_when_listed():
    claims = _claims(permissions=['inventory:read'])

    assert claims.has_permission('inventory:read')
    assert not claims.has_permission('inventory:write')


def test_roles_default_to_none():
    assert _claims().roles == []


def test_claims_cannot_be_changed():
    with pytest.raises(ValidationError):
        _claims().workspace_id = uuid.uuid4()


def test_the_token_id_is_optional():
    assert _claims().token_id is None
    assert _claims(token_id='t1').token_id == 't1'
