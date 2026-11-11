"""Service factories for the Cynthus project"""

import factory

from ...service import InventoryService, LogisticsService, ProfileService, RecipeService, ShoppingService


class InventoryServiceFactory(factory.Factory):
    class Meta:
        model = InventoryService


class ProfileServiceFactory(factory.Factory):
    class Meta:
        model = ProfileService


class ShoppingServiceFactory(factory.Factory):
    class Meta:
        model = ShoppingService


class LogisticsServiceFactory(factory.Factory):
    class Meta:
        model = LogisticsService


class RecipeServiceFactory(factory.Factory):
    class Meta:
        model = RecipeService
