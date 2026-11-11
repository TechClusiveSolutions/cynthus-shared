"""RabbitMQ connection for the Cynthus project"""

import asyncio
from os import environ


class RabbitMqConnection:
    """
        The one RabbitMQ connection of a process

        The publisher and the subscriber share it and each opens its own channel on it, so a service holds a single broker
        connection however many subscriptions it reads. The connection reconnects by itself when the broker goes away.
        ``aio_pika`` is imported on first use, so a service that runs on Service Bus does not need it installed.
    """

    def __init__(self, url: str) -> None:
        self._url = url
        self._connection = None
        self._opening = None

    @classmethod
    def from_environment(cls) -> 'RabbitMqConnection':
        """Uses RABBITMQ_URL (``amqp://user:password@host:5672/vhost``), which is a secret and never logged."""

        url = environ.get('RABBITMQ_URL')

        if not url:
            raise ValueError('RABBITMQ_URL is not set; it is required when SIGNAL_BROKER is rabbitmq')

        return cls(url)

    @staticmethod
    def errors() -> tuple:
        """What it looks like when the broker cannot be reached or refuses the connection."""

        try:
            from aio_pika.exceptions import AMQPError
        except ImportError:
            return (OSError, TimeoutError)

        return (AMQPError, OSError, TimeoutError)

    async def channel(self):
        """A new channel on the shared connection, opened (and the connection with it) when first needed."""

        connection = await self._connect()

        return await connection.channel()

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def _connect(self):
        # Created on first use so the connection can be built before an event loop is running
        if self._opening is None:
            self._opening = asyncio.Lock()

        async with self._opening:
            if self._connection is None or self._connection.is_closed:
                import aio_pika

                self._connection = await aio_pika.connect_robust(self._url)

            return self._connection
