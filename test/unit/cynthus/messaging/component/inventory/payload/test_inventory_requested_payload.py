"""Tests for cynthus.messaging.component.inventory.payload.inventory_requested_payload."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_requested_payload import InventoryRequestedPayload


def test_a_request_needs_only_its_operation():
    payload = InventoryRequestedPayload(operation='list')

    assert payload.schema_version == 1
    assert (payload.resource_id, payload.parent_id, payload.filters, payload.data) == (None, None, {}, {})


@pytest.mark.parametrize('operation', ['create', 'get', 'list', 'update', 'delete'])
def test_every_crud_operation_is_accepted(operation):
    assert InventoryRequestedPayload(operation=operation).operation == operation


def test_an_unknown_operation_is_rejected():
    with pytest.raises(ValidationError):
        InventoryRequestedPayload(operation='drop')


def test_the_operation_is_required():
    with pytest.raises(ValidationError):
        InventoryRequestedPayload()
