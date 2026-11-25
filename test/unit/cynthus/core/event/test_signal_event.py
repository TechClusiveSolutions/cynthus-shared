"""SignalEvent class unit tests for the Cynthus project"""

from datetime import datetime, timezone
from typing import ClassVar
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from cynthus.core.event import EventAction, SignalEvent


class _Meal(BaseModel):
    model_config = ConfigDict(extra='forbid')

    name: str
    servings: int = 2


class ThingHappenedEvent(SignalEvent):
    """Local subclass without a data model"""


class _TypedSignalEvent(SignalEvent):
    data_model: ClassVar[type[BaseModel] | None] = _Meal


class _ReadOnlySignalEvent(SignalEvent):
    actions: ClassVar[frozenset[EventAction] | None] = frozenset({EventAction.RETRIEVED})


def _make(cls=SignalEvent, action=EventAction.RETRIEVED, data=None, **extra):
    return cls(
        tenant_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        action=action,
        data={} if data is None else data,
        **extra,
    )


class TestSignalEvent:
    """Tests the SignalEvent fields and defaults"""

    def test_instantiation(self):
        assert isinstance(_make(), SignalEvent)

    def test_ids_are_given_as_passed(self):
        tenant_id, workspace_id, actor_id = uuid4(), uuid4(), uuid4()
        event = SignalEvent(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            actor_id=actor_id,
            action=EventAction.CREATED,
            data={'a': 1},
        )

        assert event.tenant_id == tenant_id
        assert event.workspace_id == workspace_id
        assert event.actor_id == actor_id
        assert event.action == EventAction.CREATED
        assert event.data == {'a': 1}

    def test_defaults(self):
        before = datetime.now(timezone.utc)
        event = _make()
        after = datetime.now(timezone.utc)

        assert isinstance(event.id_, UUID)
        assert isinstance(event.correlation_id, UUID)
        assert event.service_id is None
        assert event.occurred_on.tzinfo is not None
        assert before <= event.occurred_on <= after

    def test_service_id_can_be_set(self):
        service_id = uuid4()

        assert _make(service_id=service_id).service_id == service_id

    def test_two_events_get_different_ids(self):
        first, second = _make(), _make()

        assert first.id_ != second.id_
        assert first.correlation_id != second.correlation_id

    @pytest.mark.parametrize('missing', ['tenant_id', 'workspace_id', 'actor_id', 'action', 'data'])
    def test_required_field_missing_raises_validation_error(self, missing):
        values = {
            'tenant_id': uuid4(),
            'workspace_id': uuid4(),
            'actor_id': uuid4(),
            'action': EventAction.RETRIEVED,
            'data': {},
        }
        del values[missing]

        with pytest.raises(ValidationError, match=missing):
            SignalEvent(**values)

    def test_data_model_and_actions_default_to_none(self):
        assert SignalEvent.data_model is None
        assert SignalEvent.actions is None

    def test_data_model_and_actions_are_not_fields(self):
        for name in ('data_model', 'actions'):
            assert name not in SignalEvent.model_fields
            assert name not in _TypedSignalEvent.model_fields

    def test_untyped_event_accepts_any_data(self):
        assert 'anything' in _make(data={'anything': object()}).data

    def test_any_action_is_accepted_without_actions(self):
        for action in EventAction:
            assert _make(action=action).action == action


class TestSignalEventType:
    """Tests the SignalEvent.event_type property"""

    def test_signal_event_itself_is_signal(self):
        assert _make().event_type == 'signal'

    def test_subclass_name_is_snake_cased_without_trailing_event(self):
        assert _make(ThingHappenedEvent).event_type == 'thing_happened'

    def test_is_read_only(self):
        with pytest.raises(ValidationError):
            _make().event_type = 'other'

    def test_is_a_property_on_the_class(self):
        assert isinstance(SignalEvent.__dict__['event_type'], property)


class TestSignalEventDataModel:
    """Tests the optional SignalEvent.data_model validation"""

    def test_valid_data_creates_the_event(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup', 'servings': 4})

        assert event.data['name'] == 'soup'

    def test_optional_field_may_be_left_out(self):
        assert _make(_TypedSignalEvent, data={'name': 'soup'}).data['name'] == 'soup'

    def test_unknown_key_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _make(_TypedSignalEvent, data={'name': 'soup', 'colour': 'red'})

    def test_missing_required_field_raises_validation_error(self):
        with pytest.raises(ValidationError, match='name'):
            _make(_TypedSignalEvent, data={'servings': 4})

    def test_empty_data_raises_validation_error(self):
        with pytest.raises(ValidationError):
            _make(_TypedSignalEvent, data={})

    def test_wrongly_typed_field_raises_validation_error(self):
        with pytest.raises(ValidationError, match='servings'):
            _make(_TypedSignalEvent, data={'name': 'soup', 'servings': 'many'})

    def test_parsed_data_returns_the_same_object_each_time(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup', 'servings': 4})

        assert event.parsed_data(_Meal) is event.parsed_data(_Meal)
        assert event.parsed_data(_Meal).servings == 4

    def test_parsed_data_parses_once(self, monkeypatch):
        calls = []
        original = _Meal.model_validate.__func__

        def counting(cls, *args, **kwargs):
            calls.append(1)

            return original(cls, *args, **kwargs)

        monkeypatch.setattr(_Meal, 'model_validate', classmethod(counting))
        event = _make(_TypedSignalEvent, data={'name': 'soup'})
        event.parsed_data(_Meal)
        event.parsed_data(_Meal)

        assert len(calls) == 1

    def test_parsed_data_validates_for_an_untyped_event(self):
        assert _make(data={'name': 'soup'}).parsed_data(_Meal).name == 'soup'

    def test_parsed_data_for_a_model_other_than_the_declared_one(self):
        class _Name(BaseModel):
            name: str

        event = _make(_TypedSignalEvent, data={'name': 'soup'})

        assert event.parsed_data(_Name).name == 'soup'

    def test_parsed_data_refuses_invalid_data_for_the_model(self):
        with pytest.raises(ValidationError):
            _make(data={}).parsed_data(_Meal)


class TestSignalEventActions:
    """Tests the optional SignalEvent.actions check"""

    def test_allowed_action_passes(self):
        assert _make(_ReadOnlySignalEvent, action=EventAction.RETRIEVED).action == EventAction.RETRIEVED

    @pytest.mark.parametrize('action', [a for a in EventAction if a != EventAction.RETRIEVED])
    def test_other_action_raises_validation_error(self, action):
        with pytest.raises(ValidationError):
            _make(_ReadOnlySignalEvent, action=action)


class TestSignalEventFrozen:
    """Tests that a SignalEvent cannot be changed after creation"""

    def test_assigning_tenant_id_raises(self):
        event = _make()

        with pytest.raises(ValidationError):
            event.tenant_id = uuid4()

    def test_assigning_action_raises(self):
        event = _make()

        with pytest.raises(ValidationError):
            event.action = EventAction.DELETED

    def test_assigning_data_raises(self):
        event = _make()

        with pytest.raises(ValidationError):
            event.data = {'a': 1}

    def test_data_is_kept_as_a_copy_of_the_given_dict(self):
        # pydantic validates a dict into a new dict, as it does for Event: equal, not the same object
        data = {'a': 1}
        event = _make(data=data)

        assert event.data == {'a': 1}

        data['a'] = 2

        assert event.data == {'a': 1}


class TestSignalEventCopy:
    """Tests that model_copy revalidates"""

    def test_copy_with_disallowed_action_raises(self):
        event = _make(_ReadOnlySignalEvent, action=EventAction.RETRIEVED)

        with pytest.raises(ValidationError):
            event.model_copy(update={'action': EventAction.DELETED})

    def test_copy_with_allowed_action_passes(self):
        event = _make(_ReadOnlySignalEvent, action=EventAction.RETRIEVED)

        assert event.model_copy(update={'action': EventAction.RETRIEVED}).action == EventAction.RETRIEVED

    def test_copy_with_new_data_gives_new_parsed_data(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup', 'servings': 4})
        assert event.parsed_data(_Meal).name == 'soup'

        copy = event.model_copy(update={'data': {'name': 'stew', 'servings': 6}})

        assert copy.parsed_data(_Meal).name == 'stew'
        assert copy.parsed_data(_Meal).servings == 6
        assert event.parsed_data(_Meal).name == 'soup'

    def test_copy_with_invalid_data_raises(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup'})

        with pytest.raises(ValidationError):
            event.model_copy(update={'data': {'servings': 4}})

    def test_copy_with_unknown_key_raises(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup'})

        with pytest.raises(ValidationError):
            event.model_copy(update={'data': {'name': 'soup', 'colour': 'red'}})

    def test_copy_with_an_update_key_that_is_not_a_field_raises_value_error_naming_it(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup'})

        with pytest.raises(ValueError, match='bogus'):
            event.model_copy(update={'bogus': 1})

        with pytest.raises(ValueError, match='_parsed_data'):
            event.model_copy(update={'_parsed_data': None})

    def test_a_copy_without_deep_shares_nested_values_with_the_original(self):
        event = _make(data={'items': [1]})
        copy = event.model_copy()

        copy.data['items'].append(2)

        assert event.data['items'] == [1, 2]

    def test_copy_without_update_is_equal_and_keeps_id(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup'})
        copy = event.model_copy()

        assert copy == event
        assert copy.id_ == event.id_

    def test_deep_copy_is_equal_with_a_different_data_dict(self):
        event = _make(_TypedSignalEvent, data={'name': 'soup'})
        copy = event.model_copy(deep=True)

        assert copy == event
        assert copy.data is not event.data


class TestSignalEventHash:
    """Tests that a SignalEvent is hashable"""

    def test_hash_works(self):
        assert isinstance(hash(_make(data={'a': [1, 2]})), int)

    def test_equal_events_hash_equal(self):
        event = _make(data={'a': 1})
        copy = event.model_copy(deep=True)

        assert copy == event
        assert hash(copy) == hash(event)

    def test_event_in_a_set(self):
        event = _make()
        copy = event.model_copy()

        assert len({event, copy}) == 1
        assert event in {event}
        assert len({event, _make()}) == 2

    def test_event_as_dict_key(self):
        event = _make()

        assert {event: 'x'}[event.model_copy()] == 'x'
