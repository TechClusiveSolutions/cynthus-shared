"""Resource fixtures for the Cynthus project"""

from pytest import fixture

from ...resource import (
    Item,
    ItemBrand,
    StorageLocation,
    StorageLocationShelf,
    StorageShelf,
    StorageShelfItem,
)
from ..factory import (
    ItemBrandFactory,
    ItemFactory,
    StorageLocationFactory,
    StorageLocationShelfFactory,
    StorageShelfFactory,
    StorageShelfItemFactory,
)


@fixture
def item_brand() -> ItemBrand:
    return ItemBrandFactory()


@fixture
def item() -> Item:
    return ItemFactory()


@fixture
def storage_location() -> StorageLocation:
    return StorageLocationFactory()


@fixture
def storage_shelf() -> StorageShelf:
    return StorageShelfFactory()


@fixture
def storage_shelf_item() -> StorageShelfItem:
    return StorageShelfItemFactory()


@fixture
def storage_location_shelf() -> StorageLocationShelf:
    return StorageLocationShelfFactory()
