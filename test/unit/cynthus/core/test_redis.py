"""Tests for cynthus.core.redis (RedisClient)."""

import asyncio
import json

import pytest

from cynthus.core import redis as redis_module
from cynthus.core.redis import RedisClient


class FakePubSub:
    def __init__(self, server):
        self.server = server
        self.queue = asyncio.Queue()
        self.closed = False

    async def subscribe(self, channel):
        self.server.subscribers.setdefault(channel, []).append(self)

    async def unsubscribe(self, channel):
        self.server.subscribers[channel].remove(self)

    async def get_message(self, ignore_subscribe_messages=True, timeout=0):
        try:
            data = await asyncio.wait_for(self.queue.get(), timeout)
        except asyncio.TimeoutError:
            return None

        return {'type': 'message', 'data': data}

    async def aclose(self):
        self.closed = True


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.expiry = {}
        self.subscribers = {}
        self.closed = False

    async def get(self, key):
        value = self.store.get(key)

        return value.encode('utf-8') if isinstance(value, str) else value

    async def set(self, key, value, ex=None):
        self.store[key] = value
        self.expiry[key] = ex

    async def delete(self, *keys):
        return sum(self.store.pop(key, None) is not None for key in keys)

    async def exists(self, key):
        return int(key in self.store)

    async def expire(self, key, seconds):
        if key not in self.store:
            return False

        self.expiry[key] = seconds

        return True

    async def publish(self, channel, message):
        for pubsub in list(self.subscribers.get(channel, [])):
            pubsub.queue.put_nowait(message.encode('utf-8'))

        return len(self.subscribers.get(channel, []))

    def pubsub(self):
        return FakePubSub(self)

    async def ping(self):
        return True

    async def aclose(self):
        self.closed = True


@pytest.fixture(autouse=True)
def fake(monkeypatch):
    server = FakeRedis()
    opened = []

    def from_url(url, **options):
        opened.append(url)
        server.options = options

        return server

    monkeypatch.setattr(redis_module.aioredis, 'from_url', from_url)
    monkeypatch.setattr(RedisClient, 'clients', {})
    server.opened = opened

    return server


def test_clients_for_the_same_url_share_one_pool(fake):
    first, second = RedisClient('redis://one'), RedisClient('redis://one')

    assert first.client is second.client
    assert fake.opened == ['redis://one']


def test_the_pool_recovers_from_dropped_connections(fake):
    RedisClient('redis://one')

    assert fake.options['health_check_interval'] == redis_module.HEALTH_CHECK_INTERVAL_SECONDS
    assert fake.options['socket_keepalive'] is True
    assert fake.options['retry'] is not None
    assert redis_module.RedisConnectionError in fake.options['retry_on_error']
    assert redis_module.RedisTimeoutError in fake.options['retry_on_error']


def test_clients_for_different_urls_do_not_share(fake):
    RedisClient('redis://one')
    RedisClient('redis://two')

    assert fake.opened == ['redis://one', 'redis://two']


def test_from_environment_builds_the_url_and_quotes_credentials(fake, monkeypatch):
    monkeypatch.setenv('CACHE_HOST', 'cache')
    monkeypatch.setenv('CACHE_PORT', '6380')
    monkeypatch.setenv('CACHE_USERNAME', 'svc')
    monkeypatch.setenv('CACHE_PASSWORD', 'p@ss/word')
    monkeypatch.setenv('CACHE_DATABASE', '2')

    assert RedisClient.from_environment().url == 'redis://svc:p%40ss%2Fword@cache:6380/2'


def test_from_environment_without_credentials(fake, monkeypatch):
    monkeypatch.setenv('CACHE_HOST', 'cache')
    monkeypatch.delenv('CACHE_PORT', raising=False)
    monkeypatch.delenv('CACHE_USERNAME', raising=False)
    monkeypatch.delenv('CACHE_PASSWORD', raising=False)
    monkeypatch.delenv('CACHE_DATABASE', raising=False)

    assert RedisClient.from_environment().url == 'redis://cache:6379/0'


def test_from_environment_requires_a_host(monkeypatch):
    monkeypatch.delenv('CACHE_HOST', raising=False)

    with pytest.raises(ValueError):
        RedisClient.from_environment()


@pytest.mark.asyncio
@pytest.mark.parametrize('value', ['text', ['a', 1], {'a': {'b': [1, 2]}}, '{"looks": "like json"}'])
async def test_values_round_trip(value):
    client = RedisClient('redis://one')

    await client.set('key', value)

    assert await client.get('key') == value


@pytest.mark.asyncio
async def test_get_returns_the_default_for_a_missing_key():
    client = RedisClient('redis://one')

    assert await client.get('missing') is None
    assert await client.get('missing', default={}) == {}


@pytest.mark.asyncio
async def test_get_returns_text_written_by_something_else(fake):
    fake.store['raw'] = b'not json'

    assert await RedisClient('redis://one').get('raw') == 'not json'


@pytest.mark.asyncio
async def test_set_applies_the_default_expiry(fake):
    await RedisClient('redis://one').set('key', 'v')

    assert fake.expiry['key'] == 3600
    assert json.loads(fake.store['key']) == 'v'


@pytest.mark.asyncio
async def test_set_with_no_expiry_keeps_the_value(fake):
    await RedisClient('redis://one').set('key', 'v', expiry=None)

    assert fake.expiry['key'] is None


@pytest.mark.asyncio
@pytest.mark.parametrize('expiry', [0, -5])
async def test_set_rejects_a_non_positive_expiry(expiry):
    with pytest.raises(ValueError):
        await RedisClient('redis://one').set('key', 'v', expiry=expiry)


@pytest.mark.asyncio
@pytest.mark.parametrize('key', ['', None, 5])
async def test_keys_must_be_non_empty_strings(key):
    client = RedisClient('redis://one')

    with pytest.raises(ValueError):
        await client.get(key)

    with pytest.raises(ValueError):
        await client.set(key, 'v')

    with pytest.raises(ValueError):
        await client.exists(key)


@pytest.mark.asyncio
async def test_delete_and_exists():
    client = RedisClient('redis://one')
    await client.set('a', 1)
    await client.set('b', 2)

    assert await client.exists('a') is True
    assert await client.delete('a', 'b', 'c') == 2
    assert await client.exists('a') is False
    assert await client.delete() == 0


@pytest.mark.asyncio
async def test_expire(fake):
    client = RedisClient('redis://one')
    await client.set('a', 1)

    assert await client.expire('a', 30) is True
    assert fake.expiry['a'] == 30
    assert await client.expire('missing', 30) is False

    with pytest.raises(ValueError):
        await client.expire('a', 0)


@pytest.mark.asyncio
async def test_publish_encodes_the_message(fake):
    client = RedisClient('redis://one')
    pubsub = fake.pubsub()
    await pubsub.subscribe('channel')

    assert await client.publish('channel', {'a': 1}) == 1
    assert json.loads(await pubsub.queue.get()) == {'a': 1}


@pytest.mark.asyncio
async def test_get_or_wait_returns_a_stored_value():
    client = RedisClient('redis://one')
    await client.set('key', {'ready': True})

    assert await client.get_or_wait('key', 'channel', 1) == {'ready': True}


@pytest.mark.asyncio
async def test_get_or_wait_wakes_on_a_published_message():
    client = RedisClient('redis://one')

    waiter = asyncio.create_task(client.get_or_wait('key', 'channel', 5))
    await asyncio.sleep(0.05)
    await client.publish('channel', ['late'])

    assert await waiter == ['late']


@pytest.mark.asyncio
async def test_get_or_wait_times_out_and_unsubscribes(fake):
    client = RedisClient('redis://one')

    assert await client.get_or_wait('key', 'channel', 0.05) is None
    assert fake.subscribers['channel'] == []


@pytest.mark.asyncio
async def test_ping():
    assert await RedisClient('redis://one').ping() is True


@pytest.mark.asyncio
async def test_close_closes_the_pool_and_forgets_it(fake):
    client = RedisClient('redis://one')

    await client.close()

    assert fake.closed is True
    assert 'redis://one' not in RedisClient.clients
