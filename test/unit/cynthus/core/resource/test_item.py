"""Item resource class unit tests for the Cynthus project"""

from datetime import datetime

import pytest

from cynthus.core.resource import Item, ItemBrand


class TestItem:
    """Tests the item resource class"""

    def test_instantiation(self):
        """Ensure the Item class can be instantiated"""

        item = Item(
            name='Banana',
            type='food',
            brand=ItemBrand(name='Market Fresh'),
            barcode='abc123',
            expiration_date=datetime.fromisoformat('2026-11-10T00:00:00Z')
        )

        assert isinstance(item, Item)


    @pytest.mark.parametrize('action, valid', [
        ('created', True),
        ('retrieved', True),
        ('updated', True),
        ('deleted', True),
        ('added', True),
        ('removed', True),
        ('requested', False)
    ])
    def test_valid_actions(self, action: str, valid: bool):
        """Ensures the item only accepts valid actions"""

        if valid:
            item = Item(name='Apple', type='food', action=action)

            assert item.action.value == action
        else:
            with pytest.raises(ValueError):
                item = Item(name='Apple', type='food', action=action)


    @pytest.mark.parametrize('type, valid', [
        ('equipment', True),
        ('food', True),
        ('supply', True),
        ('junk', False)
    ])
    def test_valid_types(self, type: str, valid: bool):
        """Ensures the item only accepts valid types"""

        if valid:
            item = Item(name='Something', type=type)

            assert item.type.value == type
        else:
            with pytest.raises(ValueError):
                item = Item(name='Something', type=type)
