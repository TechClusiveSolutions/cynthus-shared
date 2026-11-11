import asyncio
from unittest.mock import MagicMock

import pytest

from cynthus.service import SignalConsumer


class FakeMessage:
    def __init__(self, name):
        self.name = name
        self.message_id = name


class FakeReceiver:
    """Async-iterable receiver that yields a fixed batch once and records how each message was settled."""

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


def client_for(receiver):
    client = MagicMock()
    client.get_subscription_receiver = MagicMock(return_value=receiver)

    return client


@pytest.mark.asyncio
async def test_it_listens_to_the_named_subscription_of_the_events_topic():
    receiver = FakeReceiver([])
    client = client_for(receiver)

    async def handler(message):
        pass

    await SignalConsumer(client, 'cynthus-analysis-sub', handler).run()

    client.get_subscription_receiver.assert_called_once_with(
        topic_name='cynthus-events-topic', subscription_name='cynthus-analysis-sub'
    )


@pytest.mark.asyncio
async def test_another_topic_may_be_named():
    client = client_for(FakeReceiver([]))

    async def handler(message):
        pass

    await SignalConsumer(client, 'sub', handler, topic_name='other-topic').run()

    assert client.get_subscription_receiver.call_args.kwargs['topic_name'] == 'other-topic'


@pytest.mark.asyncio
async def test_every_message_the_handler_accepts_is_completed_in_order():
    receiver, seen = FakeReceiver([FakeMessage('a'), FakeMessage('b')]), []

    async def handler(message):
        seen.append(message.name)

    await SignalConsumer(client_for(receiver), 'sub', handler).run()

    assert seen == ['a', 'b'] and [m.name for m in receiver.completed] == ['a', 'b']
    assert receiver.dead_lettered == []


@pytest.mark.asyncio
async def test_a_message_the_handler_fails_on_is_dead_lettered_and_the_loop_goes_on():
    receiver = FakeReceiver([FakeMessage('bad'), FakeMessage('good')])

    async def handler(message):
        if message.name == 'bad':
            raise ValueError('cannot read it')

    await SignalConsumer(client_for(receiver), 'sub', handler).run()

    assert [(m.name, reason) for m, reason in receiver.dead_lettered] == [('bad', 'processing_failed')]
    assert [m.name for m in receiver.completed] == ['good']


@pytest.mark.asyncio
async def test_cancellation_stops_the_loop_without_settling_the_message():
    receiver = FakeReceiver([FakeMessage('a'), FakeMessage('b')])

    async def handler(message):
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await SignalConsumer(client_for(receiver), 'sub', handler).run()

    assert receiver.completed == [] and receiver.dead_lettered == []


@pytest.mark.asyncio
async def test_a_message_without_an_id_is_still_dead_lettered():
    class Anonymous:
        pass

    receiver = FakeReceiver([Anonymous()])

    async def handler(message):
        raise RuntimeError('no')

    await SignalConsumer(client_for(receiver), 'sub', handler).run()

    assert len(receiver.dead_lettered) == 1
