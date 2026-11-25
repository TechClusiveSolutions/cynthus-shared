"""Fixtures shared by the messaging tests: a fake ``aio_pika`` so no RabbitMQ is needed."""

import sys
import types
from unittest.mock import AsyncMock, MagicMock

import pytest


class FakeMessage:
    """Stands in for ``aio_pika.Message``: keeps whatever it was built with."""

    def __init__(self, body, **properties):
        self.body = body
        self.properties = properties

    def __getattr__(self, name):
        try:
            return self.__dict__['properties'][name]
        except KeyError:
            raise AttributeError(name) from None


class FakeBroker:
    """The fake module plus the channel, exchange and queue objects its calls hand out."""

    def __init__(self):
        self.exchange = MagicMock()
        self.exchange.publish = AsyncMock()
        self.queue = MagicMock()
        self.queue.bind = AsyncMock()
        self.channel = MagicMock()
        self.channel.close = AsyncMock()
        self.channel.set_qos = AsyncMock()
        self.channel.declare_exchange = AsyncMock(return_value=self.exchange)
        self.channel.declare_queue = AsyncMock(return_value=self.queue)
        self.connection = MagicMock()
        self.connection.is_closed = False
        self.connection.channel = AsyncMock(return_value=self.channel)
        self.connection.close = AsyncMock()

        self.module = types.ModuleType('aio_pika')
        self.module.Message = FakeMessage
        self.module.ExchangeType = types.SimpleNamespace(TOPIC='topic', DIRECT='direct')
        self.module.DeliveryMode = types.SimpleNamespace(PERSISTENT=2)
        self.module.connect_robust = AsyncMock(return_value=self.connection)


@pytest.fixture
def fake_aio_pika(monkeypatch):
    broker = FakeBroker()

    monkeypatch.setitem(sys.modules, 'aio_pika', broker.module)

    return broker


@pytest.fixture
def make_event():
    """Return ``make(cls, data, **extra)``: a real event of ``cls`` built from a user, tenant and workspace."""

    from cynthus.core.event import EventAction, UserEvent
    from cynthus.core.resource import StorageLocation
    from cynthus.core.system import Tenant, Workspace
    from cynthus.core.user import User

    def make(cls, data, **extra):
        user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
        tenant = Tenant(name='T00001', owner=user, type='personal')
        workspace = Workspace(name='W00001', tenant=tenant, owner=user)
        location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)
        values = {
            'name': 'E0001', 'tenant': tenant, 'workspace': workspace, 'resource': location,
            'action': EventAction.CREATED, 'data': data,
        }

        if issubclass(cls, UserEvent):
            values['user'] = user

        return cls(**{**values, **extra})

    return make
