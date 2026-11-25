"""Tests for cynthus.service.unknown_signal_error (UnknownSignalError)."""

import pytest

from cynthus.service import UnknownSignalError
from cynthus.service.unknown_signal_error import UnknownSignalError as FromModule


def test_it_is_exported_from_the_service_package():
    assert UnknownSignalError is FromModule


def test_it_is_a_lookup_error():
    assert issubclass(UnknownSignalError, LookupError)


def test_it_is_not_a_value_error_or_a_type_error():
    assert not issubclass(UnknownSignalError, (ValueError, TypeError))


def test_it_is_built_from_a_bare_signal_name():
    error = UnknownSignalError('public.a.b.c')

    assert str(error).count('public.a.b.c') == 1
    assert str(error) != 'public.a.b.c'
    assert error.signal_name == 'public.a.b.c'


def test_it_can_be_caught_as_a_lookup_error():
    with pytest.raises(LookupError):
        raise UnknownSignalError('public.partner.service.requested')
