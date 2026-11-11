"""Tests for cynthus.messaging.subscriber.service_bus_signal_subscriber (ServiceBusSignalSubscriber)."""

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from cynthus.messaging.subscriber import ServiceBusSignalSubscriber, SignalSubscriber
from cynthus.messaging.topic import CoreSignalTopic, SignalTopic


def azure_message(name='m'):
    body = '{"n": "%s"}' % name

    return SimpleNamespace(subject='public.test.thing.created', body=[body.encode()], message_id=name,
                           correlation_id=None, application_properties=None)


class FakeReceiver:
    def __init__(self, messages):
        self._messages = list(messages)
        self.completed = []
        self.dead_lettered = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._messages:
            raise StopAsyncIteration

        return self._messages.pop(0)

    async def complete_message(self, message):
        self.completed.append(message)

    async def dead_letter_message(self, message, *, reason=None):
        self.dead_lettered.append((message, reason))


def client_for(*receivers):
    client = MagicMock()
    client.get_subscription_receiver = MagicMock(side_effect=list(receivers))

    return client


def test_it_is_a_signal_subscriber():
    assert isinstance(ServiceBusSignalSubscriber(MagicMock()), SignalSubscriber)


@pytest.mark.asyncio
async def test_handlers_get_received_signals_and_accepted_messages_are_completed():
    receiver = FakeReceiver([azure_message('a')])
    client, seen = client_for(receiver), []
    subscriber = ServiceBusSignalSubscriber(client)

    async def handler(signal):
        seen.append(signal.payload)

    subscriber.subscribe(CoreSignalTopic(), 'cynthus-sub', handler)
    await subscriber.run()

    client.get_subscription_receiver.assert_called_once_with(
        topic_name='cynthus-events-topic', subscription_name='cynthus-sub')
    assert seen == [{'n': 'a'}]
    assert len(receiver.completed) == 1


@pytest.mark.asyncio
async def test_a_handler_that_raises_dead_letters_the_message():
    receiver = FakeReceiver([azure_message('bad')])
    subscriber = ServiceBusSignalSubscriber(client_for(receiver))

    async def handler(signal):
        raise RuntimeError('boom')

    subscriber.subscribe(CoreSignalTopic(), 'sub', handler)
    await subscriber.run()

    assert receiver.completed == []
    assert [reason for _, reason in receiver.dead_lettered] == ['processing_failed']


@pytest.mark.asyncio
async def test_every_registration_is_read_on_its_own_topic_and_subscription():
    first, second = FakeReceiver([azure_message('1')]), FakeReceiver([azure_message('2')])
    client, seen = client_for(first, second), []
    subscriber = ServiceBusSignalSubscriber(client)

    async def handler(signal):
        seen.append(signal.payload['n'])

    subscriber.subscribe(CoreSignalTopic(), 'one', handler)
    subscriber.subscribe(SignalTopic(name='other-topic'), 'two', handler)
    await subscriber.run()

    calls = [call.kwargs for call in client.get_subscription_receiver.call_args_list]
    assert calls == [{'topic_name': 'cynthus-events-topic', 'subscription_name': 'one'},
                     {'topic_name': 'other-topic', 'subscription_name': 'two'}]
    assert sorted(seen) == ['1', '2']


@pytest.mark.asyncio
async def test_cancelling_run_stops_the_loops():
    class Forever(FakeReceiver):
        async def __anext__(self):
            await asyncio.Event().wait()

    async def handler(signal):
        return None

    subscriber = ServiceBusSignalSubscriber(client_for(Forever([])))
    subscriber.subscribe(CoreSignalTopic(), 'sub', handler)
    task = asyncio.create_task(subscriber.run())
    await asyncio.sleep(0)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task
