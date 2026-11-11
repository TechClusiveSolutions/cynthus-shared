"""Unit tests for the inventory list payload classes."""

import pytest

from cynthus.messaging.component.inventory.payload import InventoryListRequestedPayload, InventoryListUpdatedPayload


class TestInventoryListPayloads:
    """Tests inventory list message payloads"""

    def test_requested_payload_filters_are_optional(self):
        payload = InventoryListRequestedPayload()

        assert payload.item_type is None
        assert payload.name is None
        assert payload.schema_version == 1


    def test_requested_payload_keeps_the_filters(self):
        payload = InventoryListRequestedPayload(item_type='frozen', name='Corn')

        assert (payload.item_type, payload.name) == ('frozen', 'Corn')


    def test_updated_payload_defaults_to_an_empty_list(self):
        assert InventoryListUpdatedPayload().items == []


    def test_updated_payload_keeps_the_items(self):
        assert InventoryListUpdatedPayload(items=[{'name': 'Corn'}]).items == [{'name': 'Corn'}]
