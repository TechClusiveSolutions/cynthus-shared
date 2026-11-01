"""Tests for cynthus.messaging.bus.published_signal (PublishedSignal)."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.messaging.bus.published_signal import PublishedSignal
from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.message_base import SignalMessageBase


def make_message():
    return SignalMessageBase(event_type='public.test.thing.created', lifecycle_action=LifecycleAction.CREATED,
                             correlation_id=uuid4(), organization_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4())


def test_keeps_the_topic_name_and_the_message():
    message = make_message()
    signal = PublishedSignal(topic_name='cynthus-events-topic', message=message)

    assert signal.topic_name == 'cynthus-events-topic'
    assert signal.message is message


def test_both_fields_are_required():
    with pytest.raises(ValidationError):
        PublishedSignal(topic_name='x')

    with pytest.raises(ValidationError):
        PublishedSignal(message=make_message())


def test_is_immutable():
    signal = PublishedSignal(topic_name='x', message=make_message())

    with pytest.raises(ValidationError):
        signal.topic_name = 'y'


def test_the_access_token_is_optional_and_kept_when_given():
    assert PublishedSignal(topic_name='x', message=make_message()).access_token is None
    assert PublishedSignal(topic_name='x', message=make_message(), access_token='t').access_token == 't'
