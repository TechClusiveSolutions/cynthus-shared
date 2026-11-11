"""Tests for cynthus.messaging.subscriber.received_signal (ReceivedSignal)."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from cynthus.messaging.subscriber.received_signal import ReceivedSignal


def azure_message(**overrides):
    values = dict(
        subject='public.test.thing.created', body=[b'{"a": ', b'1}'], message_id='m-1', correlation_id='c-1',
        application_properties={b'authorization': b'Bearer abc.def.ghi'},
    )
    values.update(overrides)

    return SimpleNamespace(**values)


def test_it_is_built_from_a_service_bus_message_joining_the_body_chunks_and_decoding_bytes():
    signal = ReceivedSignal.from_service_bus(azure_message())

    assert signal.event_type == 'public.test.thing.created'
    assert signal.body == '{"a": 1}'
    assert signal.payload == {'a': 1}
    assert signal.message_id == 'm-1'
    assert signal.correlation_id == 'c-1'
    assert signal.properties == {'authorization': 'Bearer abc.def.ghi'}


def test_the_access_token_comes_without_the_bearer_prefix():
    assert ReceivedSignal.from_service_bus(azure_message()).access_token == 'abc.def.ghi'


def test_there_is_no_access_token_when_none_was_attached():
    signal = ReceivedSignal.from_service_bus(azure_message(application_properties=None))

    assert signal.properties == {}
    assert signal.access_token is None


def test_missing_ids_stay_none():
    signal = ReceivedSignal.from_service_bus(azure_message(message_id=None, correlation_id=None))

    assert signal.message_id is None
    assert signal.correlation_id is None


def test_string_properties_are_kept_as_they_are():
    signal = ReceivedSignal.from_service_bus(azure_message(application_properties={'x': 1}))

    assert signal.properties == {'x': '1'}


def test_a_signal_is_immutable():
    signal = ReceivedSignal(event_type='a.b', body='{}')

    with pytest.raises(ValidationError):
        signal.body = '[]'


def rabbitmq_message(**overrides):
    values = dict(
        type='public.test.thing.created', routing_key='public.test.thing.created', body=b'{"a": 1}',
        message_id='m-1', correlation_id='c-1', headers={'authorization': b'Bearer abc.def.ghi'},
    )
    values.update(overrides)

    return SimpleNamespace(**values)


def test_it_is_built_from_a_rabbitmq_message_decoding_the_body_and_the_header_bytes():
    signal = ReceivedSignal.from_rabbitmq(rabbitmq_message())

    assert signal.event_type == 'public.test.thing.created'
    assert signal.payload == {'a': 1}
    assert signal.message_id == 'm-1'
    assert signal.correlation_id == 'c-1'
    assert signal.access_token == 'abc.def.ghi'


def test_a_rabbitmq_message_without_a_type_falls_back_to_its_routing_key():
    signal = ReceivedSignal.from_rabbitmq(rabbitmq_message(type=None, routing_key='a.b.c'))

    assert signal.event_type == 'a.b.c'


def test_a_rabbitmq_message_may_have_no_ids_and_no_headers():
    signal = ReceivedSignal.from_rabbitmq(rabbitmq_message(message_id=None, correlation_id=None, headers=None))

    assert signal.message_id is None
    assert signal.correlation_id is None
    assert signal.properties == {}
    assert signal.access_token is None
