"""Tests for cynthus.messaging.component.inventory.payload.inventory_responded_payload."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.inventory.payload.inventory_responded_payload import InventoryRespondedPayload


def test_a_response_carries_the_operation_and_status():
    payload = InventoryRespondedPayload(operation='create', status=201, result={'id': 'x'})

    assert (payload.operation, payload.status, payload.result, payload.error) == ('create', 201, {'id': 'x'}, None)


def test_a_failure_carries_an_error():
    assert InventoryRespondedPayload(operation='get', status=404, error='not found').error == 'not found'


def test_the_operation_and_status_are_required():
    with pytest.raises(ValidationError):
        InventoryRespondedPayload()
