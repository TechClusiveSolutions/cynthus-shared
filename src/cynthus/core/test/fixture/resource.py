"""Resource fixtures for the Cynthus project"""

from pytest import fixture

from ...resource import (
    Attendee,
    Engagement,
    Item,
    ItemBrand,
    Place,
    StorageLocation,
    StorageLocationShelf,
    StorageShelf,
    StorageShelfItem,
)
from ..factory import (
    AttendeeFactory,
    EngagementFactory,
    ItemBrandFactory,
    ItemFactory,
    PlaceFactory,
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
def place() -> Place:
    return PlaceFactory()


@fixture
def attendee() -> Attendee:
    return AttendeeFactory()


@fixture
def engagement() -> Engagement:
    return EngagementFactory()


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
