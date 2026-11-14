"""Event class unit tests for the Cynthus project"""

from typing import ClassVar

import pytest
from pydantic import BaseModel, ValidationError

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
            service_id=service.id_,
            data=data
        )

        assert isinstance(event, Event)

        assert event.correlation_id is not None


    def test_event_request(self):
        pass


class TestEventType:
    """Tests the Event.event_type property"""

    @staticmethod
    def _type_of(class_name):
        cls = type(class_name, (Event,), {'__module__': __name__})

        return cls.model_construct().event_type

    def test_plain_event_class_is_event(self):
        assert Event.model_construct().event_type == 'event'

    def test_subclass_literally_named_event(self):
        assert self._type_of('Event') == 'event'

    def test_trailing_event_is_removed_and_snake_cased(self):
        assert self._type_of('InventoryLocationCreatedEvent') == 'inventory_location_created'

    def test_acronym_run_stays_together(self):
        assert self._type_of('HTTPAuthEvent') == 'http_auth'

    def test_acronym_at_the_end(self):
        assert self._type_of('UserIDEvent') == 'user_id'

    def test_only_one_trailing_event_is_removed(self):
        assert self._type_of('EventEvent') == 'event'

    def test_name_without_event_suffix_is_only_snake_cased(self):
        assert self._type_of('SomethingHappened') == 'something_happened'

    def test_event_inside_the_name_is_kept(self):
        assert self._type_of('EventLogEvent') == 'event_log'

    def test_single_word(self):
        assert self._type_of('MealEvent') == 'meal'

    def test_is_read_only(self):
        with pytest.raises(AttributeError):
            Event.model_construct().event_type = 'other'

    def test_is_a_property_on_the_class(self):
        assert isinstance(Event.__dict__['event_type'], property)


class _Meal(BaseModel):
    name: str
    servings: int = 2


class _TypedEvent(Event):
    data_model: ClassVar[type[BaseModel] | None] = _Meal


class TestDataModel:
    """Tests the optional Event.data_model validation"""

    @staticmethod
    def _make(cls, data):
        user = User(first_name='John', last_name='Doe', email='John.Doe@example.com')
        tenant = Tenant(name='T00001', owner=user, type='personal')
        workspace = Workspace(name='W00001', tenant=tenant, owner=user)
        location = StorageLocation(name='Pantry', type='ambient', workspace=workspace)

        return cls(
            name='E0001', tenant=tenant, workspace=workspace, resource=location, action=EventAction.CREATED, data=data
        )

    def test_default_is_none(self):
        assert Event.data_model is None

    def test_event_without_data_model_accepts_any_data(self):
        event = self._make(Event, {'anything': object()})

        assert 'anything' in event.data

    def test_valid_data_creates_the_event(self):
        event = self._make(_TypedEvent, {'name': 'soup', 'servings': 4})

        assert event.data['name'] == 'soup'
        assert event.data['servings'] == 4

    def test_optional_field_may_be_left_out(self):
        assert self._make(_TypedEvent, {'name': 'soup'}).data['name'] == 'soup'

    def test_missing_field_raises_validation_error(self):
        with pytest.raises(ValidationError, match='name'):
            self._make(_TypedEvent, {'servings': 4})

    def test_empty_data_raises_validation_error(self):
        with pytest.raises(ValidationError):
            self._make(_TypedEvent, {})

    def test_wrongly_typed_field_raises_validation_error(self):
        with pytest.raises(ValidationError, match='servings'):
            self._make(_TypedEvent, {'name': 'soup', 'servings': 'many'})

    def test_data_model_is_not_a_model_field(self):
        assert 'data_model' not in Event.model_fields
        assert 'data_model' not in _TypedEvent.model_fields
