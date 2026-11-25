"""Tests for cynthus.messaging.generator.signal_event_mismatch (SignalEventMismatch)."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.generator import SignalEventMismatch
from cynthus.messaging.generator.signal_event_mismatch import SignalEventMismatch as Direct


def test_is_exported_from_the_package():
    assert Direct is SignalEventMismatch


def test_is_a_value_error():
    assert issubclass(SignalEventMismatch, ValueError)
    assert not issubclass(SignalEventMismatch, ValidationError)


def test_carries_its_message():
    with pytest.raises(SignalEventMismatch, match='tenant_id') as raised:
        raise SignalEventMismatch('tenant_id of the signal is not the tenant of the token')

    assert 'tenant_id' in str(raised.value)


def test_is_caught_as_a_value_error():
    with pytest.raises(ValueError):
        raise SignalEventMismatch('actor_id')


def test_is_not_a_plain_value_error():
    assert SignalEventMismatch is not ValueError
    assert type(SignalEventMismatch('event_type')) is SignalEventMismatch
