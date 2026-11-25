"""Redis client for the Cynthus project"""

import asyncio
import json
import time
from os import environ
from typing import Any
from urllib.parse import quote

from redis import asyncio as aioredis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

Value = str | list[Any] | dict[str, Any]

DEFAULT_EXPIRY_SECONDS = 3600
HEALTH_CHECK_INTERVAL_SECONDS = 30
RETRY_ATTEMPTS = 3


class RedisClient:
    """
        Async get/set/publish abstraction over Redis

        Instances for the same URL share one connection pool. Values are stored as JSON, so strings, lists and
        dictionaries come back from `get` exactly as they went into `set`. A value that was written by something
        else and is not valid JSON comes back as its text.
    """

    clients: dict[str, aioredis.Redis] = {}

    def __init__(self, url: str) -> None:
        client = self.clients.get(url)

        if client is None:
            client = aioredis.from_url(url, **self.connection_options())

            self.clients[url] = client

        self.url = url
        self.client = client

    @staticmethod
    def connection_options() -> dict[str, Any]:
        """Pool settings that let the client survive a connection the server or network has dropped.

        Idle connections are checked before reuse and kept alive at the socket level, and a command that fails
        on a broken connection is retried (on a fresh connection) with a short backoff.
        """

        return {
            'health_check_interval': HEALTH_CHECK_INTERVAL_SECONDS,
            'socket_keepalive': True,
            'retry': Retry(ExponentialBackoff(cap=1, base=0.05), RETRY_ATTEMPTS),
            'retry_on_error': [RedisConnectionError, RedisTimeoutError],
        }

    @classmethod
    def from_environment(cls) -> 'RedisClient':
        """Build a client from the CACHE_HOST, CACHE_PORT, CACHE_USERNAME, CACHE_PASSWORD and CACHE_DATABASE settings."""

        host = environ.get('CACHE_HOST')
        port = environ.get('CACHE_PORT', '6379')
        database = environ.get('CACHE_DATABASE', '0')
        username = quote(environ.get('CACHE_USERNAME', ''), safe='')
        password = quote(environ.get('CACHE_PASSWORD', ''), safe='')

        if not host:
            raise ValueError('CACHE_HOST is not set')

        credentials = f'{username}:{password}@' if username or password else ''

        return cls(f'redis://{credentials}{host}:{port}/{database}')

    @staticmethod
    def _encode(value: Value) -> str:
        return json.dumps(value)

    @staticmethod
    def _decode(raw: bytes | str | None) -> Value | None:
        if raw is None:
            return None

        text = raw.decode('utf-8') if isinstance(raw, bytes) else raw

        try:
            return json.loads(text)
        except ValueError:
            return text

    @staticmethod
    def _check_key(key: str) -> None:
        if not isinstance(key, str) or not key:
            raise ValueError('A Redis key must be a non-empty string')

    async def get(self, key: str, default: Value | None = None) -> Value | None:
        """Return the value stored at `key`, or `default` when there is none."""

        self._check_key(key)

        value = self._decode(await self.client.get(key))

        return default if value is None else value

    async def set(self, key: str, value: Value, expiry: int | None = DEFAULT_EXPIRY_SECONDS) -> None:
        """Store `value` at `key`. It expires after `expiry` seconds; pass None to keep it until it is deleted."""

        self._check_key(key)

        if expiry is not None and expiry <= 0:
            raise ValueError('expiry must be a positive number of seconds or None')

        await self.client.set(key, self._encode(value), ex=expiry)

    async def delete(self, *keys: str) -> int:
        """Remove the keys and return how many existed."""

        for key in keys:
            self._check_key(key)

        return await self.client.delete(*keys) if keys else 0

    async def exists(self, key: str) -> bool:
        self._check_key(key)

        return bool(await self.client.exists(key))

    async def expire(self, key: str, expiry: int) -> bool:
        """Set a new lifetime for `key`; returns False when the key does not exist."""

        self._check_key(key)

        if expiry <= 0:
            raise ValueError('expiry must be a positive number of seconds')

        return bool(await self.client.expire(key, expiry))

    async def publish(self, channel: str, message: Value) -> int:
        """Send `message` to every subscriber of `channel` and return how many received it."""

        self._check_key(channel)

        return await self.client.publish(channel, self._encode(message))

    async def get_or_wait(self, key: str, channel: str, timeout: float) -> Value | None:
        """Return the value at `key`, or the next message on `channel`, or None after `timeout` seconds.

        Subscribes before it reads the key so that a value published in between is never missed.
        """

        self._check_key(key)
        self._check_key(channel)

        pubsub = self.client.pubsub()

        await pubsub.subscribe(channel)

        try:
            stored = await self.get(key)

            if stored is not None:
                return stored

            deadline = time.monotonic() + timeout

            while (remaining := deadline - time.monotonic()) > 0:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=min(remaining, 1.0))

                if message is not None:
                    return self._decode(message['data'])

                await asyncio.sleep(0)

            return None
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()

    async def ping(self) -> bool:
        return bool(await self.client.ping())

    async def close(self) -> None:
        """Close the shared connection pool; the next client for this URL opens a new one."""

        if self.clients.get(self.url) is self.client:
            del self.clients[self.url]

        await self.client.aclose()
