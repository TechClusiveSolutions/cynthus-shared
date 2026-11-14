"""Tests for cynthus.messaging.registry.unknown_event_error (UnknownEventError)."""

import pytest

from cynthus.messaging.registry import UnknownEventError
from cynthus.messaging.registry.unknown_event_error import UnknownEventError as Direct


def test_is_exported_from_the_package():
    assert Direct is UnknownEventError


def test_is_a_lookup_error():
    assert issubclass(UnknownEventError, LookupError)


def test_message_is_kept():
    assert 'SomeEvent' in str(UnknownEventError('No signal registered for SomeEvent'))


def test_can_be_raised_and_caught_as_lookup_error():
    with pytest.raises(LookupError):
        raise UnknownEventError('x')
