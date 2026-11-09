import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.exceptions import ServiceRequestError
from azure.servicebus.exceptions import ServiceBusConnectionError

from cynthus.messaging.publisher import ServiceBusSignalPublisher, SignalBusUnavailable, SignalPublisher
from cynthus.messaging.publisher import service_bus_signal_publisher as publisher_module
from cynthus.messaging.topic import CoreSignalTopic, SignalTopic


def _client():
    sent = []
    sender = MagicMock()
    sender.send_messages = AsyncMock(side_effect=lambda message: sent.append(message))
    sender.__aenter__ = AsyncMock(return_value=sender)
    sender.__aexit__ = AsyncMock(return_value=False)
    client = MagicMock()
    client.get_topic_sender = MagicMock(return_value=sender)
    client.close = AsyncMock()

    return client, sent


def _message():
    message = MagicMock()
    message.model_dump_json.return_value = '{"event_type": "audit.identity.token.issued"}'
    message.event_type = 'audit.identity.token.issued'
    message.correlation_id = 'corr-1'

    return message


@pytest.mark.asyncio
async def test_a_signal_goes_to_the_events_topic_addressed_by_its_event_type():
    client, sent = _client()

    await ServiceBusSignalPublisher(client).publish(_message())

    client.get_topic_sender.assert_called_once_with(topic_name='cynthus-events-topic')
    assert sent[0].subject == 'audit.identity.token.issued'
    assert sent[0].correlation_id == 'corr-1'
    assert sent[0].application_properties is None


@pytest.mark.asyncio
async def test_the_callers_token_travels_as_a_property_never_in_the_body():
    client, sent = _client()

    await ServiceBusSignalPublisher(client).publish(_message(), access_token='abc.def.ghi')

    assert sent[0].application_properties == {'authorization': 'Bearer abc.def.ghi'}
    assert 'abc.def.ghi' not in str(sent[0])


def test_a_connection_string_selects_the_emulator_client(monkeypatch):
    monkeypatch.setenv('SERVICE_BUS_CONNECTION_STRING', 'Endpoint=sb://x')

    with patch.object(publisher_module, 'ServiceBusClient') as bus:
        publisher = ServiceBusSignalPublisher.from_environment()

    bus.from_connection_string.assert_called_once_with('Endpoint=sb://x')
    assert publisher._client is bus.from_connection_string.return_value
    assert publisher._credential is None


@pytest.mark.asyncio
async def test_without_a_connection_string_the_namespace_and_azure_credentials_are_used(monkeypatch):
    monkeypatch.delenv('SERVICE_BUS_CONNECTION_STRING', raising=False)
    monkeypatch.setenv('SERVICE_BUS_NAMESPACE', 'bus.test.servicebus.windows.net')

    with patch.object(publisher_module, 'ServiceBusClient') as bus, \
            patch.object(publisher_module, 'DefaultAzureCredential') as credential:
        credential.return_value.close = AsyncMock()
        bus.return_value.close = AsyncMock()
        publisher = ServiceBusSignalPublisher.from_environment()

        await publisher.close()

    assert bus.call_args.kwargs == {
        'fully_qualified_namespace': 'bus.test.servicebus.windows.net', 'credential': credential.return_value,
    }
    credential.return_value.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_closes_the_client():
    client, _ = _client()

    await ServiceBusSignalPublisher(client).close()

    client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_one_sender_is_opened_and_reused_for_every_message():
    client, sent = _client()
    publisher = ServiceBusSignalPublisher(client)

    for _ in range(3):
        await publisher.publish(_message())

    assert len(sent) == 3
    client.get_topic_sender.assert_called_once_with(topic_name='cynthus-events-topic')
    client.get_topic_sender.return_value.__aenter__.assert_awaited_once()
    client.get_topic_sender.return_value.__aexit__.assert_not_awaited()


@pytest.mark.asyncio
async def test_messages_published_together_still_share_one_sender():
    import asyncio

    client, sent = _client()
    publisher = ServiceBusSignalPublisher(client)

    await asyncio.gather(*(publisher.publish(_message()) for _ in range(5)))

    assert len(sent) == 5
    client.get_topic_sender.assert_called_once()


@pytest.mark.asyncio
async def test_a_dropped_link_is_replaced_and_the_message_is_sent_again():
    client, sent = _client()
    sender = client.get_topic_sender.return_value
    calls = {'count': 0}

    async def flaky(message):
        calls['count'] += 1

        if calls['count'] == 2:
            raise RuntimeError('link detached')

        sent.append(message)

    sender.send_messages = AsyncMock(side_effect=flaky)
    publisher = ServiceBusSignalPublisher(client)

    await publisher.publish(_message())
    await publisher.publish(_message())

    assert len(sent) == 2
    assert client.get_topic_sender.call_count == 2
    sender.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_a_failure_on_the_fresh_sender_is_raised():
    client, _ = _client()
    client.get_topic_sender.return_value.send_messages = AsyncMock(side_effect=RuntimeError('bus is down'))

    with pytest.raises(RuntimeError, match='bus is down'):
        await ServiceBusSignalPublisher(client).publish(_message())

    assert client.get_topic_sender.call_count == 2


@pytest.mark.asyncio
async def test_close_closes_the_open_sender_before_the_client():
    client, _ = _client()
    publisher = ServiceBusSignalPublisher(client)
    await publisher.publish(_message())

    await publisher.close()

    client.get_topic_sender.return_value.__aexit__.assert_awaited_once()
    client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_a_sender_that_will_not_close_does_not_stop_the_close():
    client, _ = _client()
    publisher = ServiceBusSignalPublisher(client)
    await publisher.publish(_message())
    client.get_topic_sender.return_value.__aexit__ = AsyncMock(side_effect=RuntimeError('already closed'))

    await publisher.close()

    client.close.assert_awaited_once()


def test_everyone_who_shares_a_client_shares_its_publisher():
    client, _ = _client()
    other, _ = _client()

    assert ServiceBusSignalPublisher.for_client(client) is ServiceBusSignalPublisher.for_client(client)
    assert ServiceBusSignalPublisher.for_client(client) is not ServiceBusSignalPublisher.for_client(other)
    assert ServiceBusSignalPublisher.for_client(client)._client is client


@pytest.mark.asyncio
async def test_a_shared_publisher_keeps_one_sender_across_callers():
    client, sent = _client()

    await ServiceBusSignalPublisher.for_client(client).publish(_message())
    await ServiceBusSignalPublisher.for_client(client).publish(_message())

    assert len(sent) == 2
    client.get_topic_sender.assert_called_once()


def test_a_publisher_and_its_client_are_released_together():
    import gc
    import weakref

    class Client:
        pass

    client = Client()
    reference = weakref.ref(ServiceBusSignalPublisher.for_client(client))

    del client
    gc.collect()

    assert reference() is None


def _tracking_client():
    """A client whose senders record how many sends run at once and which were closed."""

    state = {'senders': [], 'active': 0, 'peak': 0}

    def make_sender(**_):
        sender = MagicMock()
        sender.closed = False

        async def send(message):
            state['active'] += 1
            state['peak'] = max(state['peak'], state['active'])
            await asyncio.sleep(0.01)
            state['active'] -= 1

        async def close(*_):
            sender.closed = True

        sender.send_messages = AsyncMock(side_effect=send)
        sender.__aenter__ = AsyncMock(return_value=sender)
        sender.__aexit__ = AsyncMock(side_effect=close)
        state['senders'].append(sender)

        return sender

    client = MagicMock()
    client.get_topic_sender = MagicMock(side_effect=make_sender)

    return client, state


@pytest.mark.asyncio
async def test_overlapping_publishes_share_one_sender_and_never_send_at_once():
    client, state = _tracking_client()
    publisher = ServiceBusSignalPublisher(client)

    await asyncio.gather(*(publisher.publish(_message()) for _ in range(5)))

    assert len(state['senders']) == 1
    assert state['peak'] == 1
    assert state['senders'][0].send_messages.await_count == 5


@pytest.mark.asyncio
async def test_a_failed_send_retries_on_a_new_sender_and_closes_the_failed_one():
    client, state = _tracking_client()
    publisher = ServiceBusSignalPublisher(client)

    await publisher.publish(_message())
    state['senders'][0].send_messages.side_effect = RuntimeError('link dropped')

    await publisher.publish(_message())

    first, second = state['senders']
    assert first.closed
    assert not second.closed
    second.send_messages.assert_awaited_once()


@pytest.mark.asyncio
async def test_overlapping_publishes_after_a_failure_leave_one_open_sender():
    client, state = _tracking_client()
    publisher = ServiceBusSignalPublisher(client)

    await publisher.publish(_message())
    state['senders'][0].send_messages.side_effect = RuntimeError('link dropped')

    await asyncio.gather(*(publisher.publish(_message()) for _ in range(4)))

    assert [sender.closed for sender in state['senders']].count(False) == 1


@pytest.mark.asyncio
async def test_a_sender_that_fails_to_open_is_closed_not_orphaned():
    client, state = _tracking_client()
    sender_factory = client.get_topic_sender.side_effect

    def failing(**kwargs):
        sender = sender_factory(**kwargs)
        sender.__aenter__ = AsyncMock(side_effect=RuntimeError('quota'))

        return sender

    client.get_topic_sender.side_effect = failing

    with pytest.raises(RuntimeError):
        await ServiceBusSignalPublisher(client).publish(_message())

    assert all(sender.closed for sender in state['senders'])


@pytest.mark.asyncio
async def test_discarding_a_stale_sender_does_not_close_the_current_one():
    client, state = _tracking_client()
    publisher = ServiceBusSignalPublisher(client)
    await publisher.publish(_message())
    current = state['senders'][0]
    stale = MagicMock()
    stale.__aexit__ = AsyncMock(return_value=False)

    await publisher._discard(stale)

    stale.__aexit__.assert_awaited_once()
    assert not current.closed
    assert publisher._sender is current


def test_it_is_a_signal_publisher():
    assert isinstance(ServiceBusSignalPublisher(MagicMock()), SignalPublisher)


@pytest.mark.asyncio
async def test_the_core_topic_may_be_named_but_another_topic_is_refused():
    client, sent = _client()
    publisher = ServiceBusSignalPublisher(client)

    await publisher.publish(_message(), topic=CoreSignalTopic())

    with pytest.raises(ValueError):
        await publisher.publish(_message(), topic=SignalTopic(name='other'))

    assert len(sent) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('error', [
    ServiceBusConnectionError(message='ConnectionsQuotaExceeded for namespace secret-namespace'),
    ServiceRequestError('cannot reach the namespace'),
    ConnectionRefusedError('refused'),
    TimeoutError('timed out'),
])
async def test_a_bus_that_cannot_be_reached_is_signal_bus_unavailable(error, caplog):
    client, _ = _client()
    client.get_topic_sender.return_value.send_messages = AsyncMock(side_effect=error)

    with pytest.raises(SignalBusUnavailable) as raised:
        await ServiceBusSignalPublisher(client).publish(_message())

    assert raised.value.__cause__ is error
    assert 'secret-namespace' not in str(raised.value)
    assert 'secret-namespace' not in caplog.text
    assert client.get_topic_sender.call_count == 2


@pytest.mark.asyncio
async def test_a_sender_that_cannot_be_opened_is_signal_bus_unavailable():
    client, _ = _client()
    client.get_topic_sender.return_value.__aenter__ = AsyncMock(side_effect=ServiceBusConnectionError(message='down'))

    with pytest.raises(SignalBusUnavailable):
        await ServiceBusSignalPublisher(client).publish(_message())


@pytest.mark.asyncio
async def test_other_errors_are_not_mistaken_for_an_unavailable_bus():
    client, _ = _client()
    client.get_topic_sender.return_value.send_messages = AsyncMock(side_effect=ValueError('bad message'))

    with pytest.raises(ValueError):
        await ServiceBusSignalPublisher(client).publish(_message())


@pytest.mark.asyncio
async def test_a_send_that_hangs_gives_up_after_the_time_limit(monkeypatch):
    monkeypatch.setattr(publisher_module, 'SEND_TIMEOUT_SECONDS', 0.05)
    client, _ = _client()
    never = asyncio.Event()

    async def hang(message):
        await never.wait()

    client.get_topic_sender.return_value.send_messages = hang

    with pytest.raises(SignalBusUnavailable):
        await asyncio.wait_for(ServiceBusSignalPublisher(client).publish(_message()), 2)

    assert client.get_topic_sender.call_count == 2


@pytest.mark.asyncio
async def test_after_a_failure_the_publisher_refuses_at_once_for_the_cooldown(monkeypatch):
    client, _ = _client()
    client.get_topic_sender.return_value.send_messages = AsyncMock(side_effect=ServiceBusConnectionError(message='down'))
    publisher = ServiceBusSignalPublisher(client)

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())

    calls = client.get_topic_sender.call_count

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())

    assert client.get_topic_sender.call_count == calls


@pytest.mark.asyncio
async def test_callers_queued_behind_a_failing_send_do_not_each_try_again():
    client, _ = _client()
    client.get_topic_sender.return_value.send_messages = AsyncMock(side_effect=ServiceBusConnectionError(message='down'))
    publisher = ServiceBusSignalPublisher(client)

    results = await asyncio.gather(*(publisher.publish(_message()) for _ in range(5)), return_exceptions=True)

    assert all(isinstance(result, SignalBusUnavailable) for result in results)
    assert client.get_topic_sender.call_count == 2


@pytest.mark.asyncio
async def test_the_publisher_tries_the_bus_again_once_the_cooldown_has_passed(monkeypatch):
    client, sent = _client()
    send = client.get_topic_sender.return_value.send_messages
    publisher = ServiceBusSignalPublisher(client)
    publisher._down_until = time.monotonic() + 1000

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())

    assert sent == []

    publisher._down_until = time.monotonic() - 1
    await publisher.publish(_message())

    assert len(sent) == 1
    send.assert_awaited()


@pytest.mark.asyncio
async def test_an_unreachable_bus_is_reported_and_a_failing_report_changes_nothing():
    client, _ = _client()
    client.get_topic_sender.return_value.send_messages = AsyncMock(side_effect=ServiceBusConnectionError(message='down'))
    reported = []

    async def report():
        reported.append(True)

    publisher = ServiceBusSignalPublisher(client)
    publisher.on_unavailable = report

    with pytest.raises(SignalBusUnavailable):
        await publisher.publish(_message())

    assert reported == [True]

    async def broken():
        raise RuntimeError('redis is down')

    other = ServiceBusSignalPublisher(client)
    other.on_unavailable = broken

    with pytest.raises(SignalBusUnavailable):
        await other.publish(_message())


@pytest.mark.asyncio
async def test_nothing_is_reported_when_the_publish_succeeds():
    client, _ = _client()
    reported = []

    async def report():
        reported.append(True)

    publisher = ServiceBusSignalPublisher(client)
    publisher.on_unavailable = report

    await publisher.publish(_message())

    assert reported == []
