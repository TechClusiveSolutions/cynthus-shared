"""Event class unit tests for the Cynthus project"""

import pytest

from datetime import datetime, timezone

from cynthus.core.event import Event, EventAction
from cynthus.core.resource import StorageLocation
from cynthus.core.service import InventoryService
from cynthus.core.system import Tenant, Workspace
from cynthus.core.user import User


class TestEvent:
    """Tests the Event class"""

    def test_instantiation(self):
        """Ensure the Event class can be instantiated"""

        user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
        tenant = Tenant(name='T00001', owner=user, type='personal')
        workspace = Workspace(name='W00001', tenant=tenant, owner=user)
        location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)
        service = InventoryService()

        data= {
            'requestor': {
                'user_id': user.id_
            }
        }

        event = Event(
            name='E0001',
            tenant=tenant,
            workspace=workspace,
            resource=location,
            action=EventAction.CREATED,
            actor=service,
            data=data
        )

        assert isinstance(event, Event)

        assert event.correlation_id is not None


    def test_event_request(self):
        pass
        