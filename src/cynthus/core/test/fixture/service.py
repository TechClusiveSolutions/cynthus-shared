"""Service fixtures for the Cynthus project"""

from pytest import fixture

from ...service import (
    InventoryService,
    LogisticsService,
    ProfileService,
    RecipeService,
    ShoppingService,
)
from ..factory import (
    InventoryServiceFactory,
    LogisticsServiceFactory,
    ProfileServiceFactory,
    RecipeServiceFactory,
    ShoppingServiceFactory,
)


@fixture
def inventory_service() -> InventoryService:
    return InventoryServiceFactory()


@fixture
def profile_service() -> ProfileService:
    return ProfileServiceFactory()


@fixture
def shopping_service() -> ShoppingService:
    return ShoppingServiceFactory()


@fixture
def logistics_service() -> LogisticsService:
    return LogisticsServiceFactory()


@fixture
def recipe_service() -> RecipeService:
    return RecipeServiceFactory()
