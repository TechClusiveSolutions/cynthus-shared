import pytest

from cynthus.security import BearerToken, TokenError


def test_the_token_is_taken_from_a_bearer_header():
    assert BearerToken.extract('Bearer abc.def.ghi') == 'abc.def.ghi'


def test_the_scheme_is_case_insensitive_and_whitespace_is_trimmed():
    assert BearerToken.extract('  bEaReR   abc  ') == 'abc'


def test_a_header_from_a_message_property_may_be_bytes():
    assert BearerToken.extract(b'Bearer abc') == 'abc'


@pytest.mark.parametrize('header', [None, '', b''])
def test_a_missing_header_is_rejected(header):
    with pytest.raises(TokenError, match='missing'):
        BearerToken.extract(header)


@pytest.mark.parametrize('header', ['Basic abc', 'Bearer', 'Bearer   ', 'abc'])
def test_another_scheme_or_no_token_is_rejected(header):
    with pytest.raises(TokenError, match='malformed'):
        BearerToken.extract(header)
