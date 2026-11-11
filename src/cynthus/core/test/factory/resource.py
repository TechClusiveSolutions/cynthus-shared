"""Resource factories for the Cynthus project"""

from datetime import datetime, timezone

import factory

from ...resource import (
    Attendee,
    Engagement,
    Item,
    ItemBrand,
    ItemType,
    Place,
    StorageLocation,
    StorageLocationShelf,
    StorageLocationType,
    StorageShelf,
    StorageShelfItem,
)
from .system import WorkspaceFactory


class ItemBrandFactory(factory.Factory):
    class Meta:
        model = ItemBrand

    name = factory.Sequence(lambda n: f'Brand {n}')


class ItemFactory(factory.Factory):
    class Meta:
        model = Item

    name = factory.Sequence(lambda n: f'Item {n}')
    type = ItemType.FOOD


class PlaceFactory(factory.Factory):
    class Meta:
        model = Place

    name = factory.Sequence(lambda n: f'Place {n}')
    workspace = factory.SubFactory(WorkspaceFactory)
    city = 'Dallas'


class AttendeeFactory(factory.Factory):
    class Meta:
        model = Attendee

    name = factory.Sequence(lambda n: f'Guest {n}')


class EngagementFactory(factory.Factory):
    class Meta:
        model = Engagement

    name = factory.Sequence(lambda n: f'Engagement {n}')
    workspace = factory.SubFactory(WorkspaceFactory)
    starts_at = datetime(2026, 12, 5, 18, 0, tzinfo=timezone.utc)
    ends_at = datetime(2026, 12, 5, 21, 0, tzinfo=timezone.utc)


class StorageLocationFactory(factory.Factory):
    class Meta:
        model = StorageLocation

    name = factory.Sequence(lambda n: f'Location {n}')
    type = StorageLocationType.AMBIENT
    workspace = factory.SubFactory(WorkspaceFactory)


class StorageShelfFactory(factory.Factory):
    class Meta:
        model = StorageShelf

    name = factory.Sequence(lambda n: f'Shelf {n}')
    workspace = factory.SubFactory(WorkspaceFactory)
    temperature_high = 25.0
    temperature_low = 15.0
    temperature_average = 20.0
    temperature_unit = 'C'


class StorageShelfItemFactory(factory.Factory):
    class Meta:
        model = StorageShelfItem

    shelf = factory.SubFactory(StorageShelfFactory)
    item = factory.SubFactory(ItemFactory)


class StorageLocationShelfFactory(factory.Factory):
    class Meta:
        model = StorageLocationShelf

    location = factory.SubFactory(StorageLocationFactory)
    shelf = factory.SubFactory(StorageShelfFactory, workspace=factory.SelfAttribute('..location.workspace'))
    position = '1'
