"""event_type_name helper unit tests for the Cynthus project"""

import pytest

from cynthus.core.event import Event, SignalEvent
from cynthus.core.event.event_type_name import event_type_name


class TestEventTypeName:
    """Tests the event_type_name helper"""

    @pytest.mark.parametrize(
        ('class_name', 'expected'),
        [
            ('InventoryLocationCreatedEvent', 'inventory_location_created'),
            ('ThingHappenedEvent', 'thing_happened'),
            ('MealEvent', 'meal'),
            ('HTTPServerEvent', 'http_server'),
            ('HTTPAuthEvent', 'http_auth'),
            ('UserIDEvent', 'user_id'),
            ('Version2UpdatedEvent', 'version2_updated'),
            ('Step10DoneEvent', 'step10_done'),
            ('SomethingHappened', 'something_happened'),
            ('Event', 'event'),
            ('SignalEvent', 'signal'),
            ('EventEvent', 'event'),
            ('EventLogEvent', 'event_log'),
        ],
    )
    def test_names(self, class_name, expected):
        assert event_type_name(class_name) == expected

    def test_event_type_agrees_with_helper_for_event_subclass(self):
        cls = type('InventoryShelfCreatedEvent', (Event,), {'__module__': __name__})

        assert cls.model_construct().event_type == event_type_name('InventoryShelfCreatedEvent')

    def test_event_type_agrees_with_helper_for_signal_event_subclass(self):
        cls = type('HTTPServerEvent', (SignalEvent,), {'__module__': __name__})

        assert cls.model_construct().event_type == event_type_name('HTTPServerEvent')

    def test_event_type_agrees_with_helper_for_base_classes(self):
        assert Event.model_construct().event_type == event_type_name('Event')
        assert SignalEvent.model_construct().event_type == event_type_name('SignalEvent')
