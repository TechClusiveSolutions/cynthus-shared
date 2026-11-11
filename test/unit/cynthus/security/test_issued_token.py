import pytest
from pydantic import ValidationError

from cynthus.security import IssuedToken


def test_an_issued_token_keeps_its_facts():
    issued = IssuedToken(token='a.b.c', token_id='t1', key_id='k1', expires_in=60)

    assert (issued.token, issued.token_id, issued.key_id, issued.expires_in) == ('a.b.c', 't1', 'k1', 60)


def test_an_issued_token_cannot_be_changed():
    with pytest.raises(ValidationError):
        IssuedToken(token='a', token_id='t', key_id='k', expires_in=1).token = 'b'
