"""Received Signal class for the Cynthus project"""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

AUTHORIZATION = 'authorization'


def _text(value) -> str:
    return value.decode('utf-8') if isinstance(value, bytes) else str(value)


class ReceivedSignal(BaseModel):
    """
        One signal as a handler sees it, whatever broker delivered it

        ``body`` is the JSON text of the message. ``properties`` carries what travels beside the body, such as the
        ``authorization`` bearer token, which is never part of the body.
    """

    model_config = ConfigDict(frozen=True)

    event_type: str
    body: str
    message_id: str | None = None
    correlation_id: str | None = None
    properties: dict[str, str] = Field(default_factory=dict)

    @property
    def payload(self) -> dict[str, Any]:
        """The decoded JSON body."""

        return json.loads(self.body)

    @property
    def access_token(self) -> str | None:
        """The bearer token the publisher attached, without the ``Bearer`` prefix."""

        value = self.properties.get(AUTHORIZATION)

        if value is None:
            return None

        return value.removeprefix('Bearer ')

    @classmethod
    def from_service_bus(cls, message) -> 'ReceivedSignal':
        """Builds the signal from an Azure ``ServiceBusReceivedMessage`` (keys and values may arrive as bytes)."""

        properties = {_text(key): _text(value) for key, value in (message.application_properties or {}).items()}

        return cls(
            event_type=_text(message.subject),
            body=b''.join(message.body).decode('utf-8'),
            message_id=None if message.message_id is None else _text(message.message_id),
            correlation_id=None if message.correlation_id is None else _text(message.correlation_id),
            properties=properties,
        )
