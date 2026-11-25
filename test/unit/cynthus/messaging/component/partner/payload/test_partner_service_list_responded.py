"""Tests for cynthus.messaging.component.partner.payload.partner_service_list_responded."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.partner.payload.partner_service_list_item import PartnerServiceListItem
from cynthus.messaging.component.partner.payload.partner_service_list_responded import (
    PartnerServiceListRespondedPayload,
)


def make_items():
    return [
        PartnerServiceListItem(id=uuid4(), name='Acme Plumbing'),
        PartnerServiceListItem(id=uuid4(), name='Best Cleaning'),
    ]


def test_the_defaults():
    payload = PartnerServiceListRespondedPayload(status=200)

    assert payload.schema_version == 1
    assert payload.result is None
    assert payload.error is None


def test_status_is_required():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedPayload()


@pytest.mark.parametrize('status', ['ok', None, 'abc', 1.5, [200]])
def test_a_non_integer_status_is_rejected(status):
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedPayload(status=status)


@pytest.mark.parametrize('status', [200, 401, 403, 422, 404, 500, 0, -1])
def test_status_has_no_range_check(status):
    assert PartnerServiceListRespondedPayload(status=status).status == status


def test_an_empty_result_is_kept_distinct_from_none():
    payload = PartnerServiceListRespondedPayload(status=200, result=[])

    assert payload.result == []


def test_result_rejects_a_bad_item():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedPayload(status=200, result=[{'id': 'x', 'name': 'a'}])


def test_result_rejects_a_non_list():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedPayload(status=200, result='nope')


def test_error_rejects_a_non_string():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedPayload(status=422, error=['bad'])


def test_round_trips_with_two_items():
    payload = PartnerServiceListRespondedPayload(status=200, result=make_items())

    restored = PartnerServiceListRespondedPayload.model_validate_json(payload.model_dump_json())

    assert restored == payload
    assert len(restored.result) == 2
    assert all(isinstance(item, PartnerServiceListItem) for item in restored.result)


def test_round_trips_with_an_error_and_no_result():
    payload = PartnerServiceListRespondedPayload(status=403, result=None, error='forbidden')

    restored = PartnerServiceListRespondedPayload.model_validate_json(payload.model_dump_json())

    assert restored == payload
    assert restored.result is None
    assert restored.error == 'forbidden'
