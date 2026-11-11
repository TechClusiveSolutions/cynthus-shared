from cynthus.security import TokenError


def test_the_reason_is_kept_and_used_as_the_message():
    error = TokenError('token expired')

    assert error.reason == 'token expired'
    assert str(error) == 'token expired'
