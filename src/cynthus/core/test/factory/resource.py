"""Resource factories for the Cynthus project"""

import factory

from ...resource import (
    Item,
    ItemBrand,
    ItemType,
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
