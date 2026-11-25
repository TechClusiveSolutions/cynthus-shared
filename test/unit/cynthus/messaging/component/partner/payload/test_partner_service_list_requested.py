"""Tests for cynthus.messaging.component.partner.payload.partner_service_list_requested."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.partner.payload.partner_service_list_filters import PartnerServiceListFilters
from cynthus.messaging.component.partner.payload.partner_service_list_requested import (
    PartnerServiceListRequestedPayload,
)


def test_a_request_needs_no_arguments():
    payload = PartnerServiceListRequestedPayload()

    assert payload.schema_version == 1
    assert payload.filters == PartnerServiceListFilters()
    assert payload.filters.name is None


def test_each_request_gets_its_own_filters():
    assert PartnerServiceListRequestedPayload().filters is not PartnerServiceListRequestedPayload().filters


def test_a_request_accepts_a_name_filter():
    payload = PartnerServiceListRequestedPayload(filters={'name': 'acme'})

    assert payload.filters.name == 'acme'


def test_a_request_accepts_a_filters_object():
    payload = PartnerServiceListRequestedPayload(filters=PartnerServiceListFilters(name='acme'))

    assert payload.filters.name == 'acme'


def test_a_request_accepts_empty_filters_mapping():
    assert PartnerServiceListRequestedPayload(filters={}).filters.name is None


def test_a_request_rejects_a_non_string_name():
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedPayload(filters={'name': 5})


def test_a_request_rejects_an_unknown_filter_key():
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedPayload(filters={'colour': 'red'})


@pytest.mark.parametrize('filters', [None, 'acme', [], 5])
def test_a_request_rejects_filters_of_the_wrong_type(filters):
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedPayload(filters=filters)


@pytest.mark.parametrize('version', [0, -1])
def test_a_schema_version_below_one_is_rejected(version):
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedPayload(schema_version=version)


def test_a_higher_schema_version_is_accepted():
    assert PartnerServiceListRequestedPayload(schema_version=2).schema_version == 2


def test_a_non_integer_schema_version_is_rejected():
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedPayload(schema_version='x')


def test_round_trips_through_json():
    payload = PartnerServiceListRequestedPayload(filters={'name': 'acme'})

    assert PartnerServiceListRequestedPayload.model_validate_json(payload.model_dump_json()) == payload


def test_default_round_trips_through_json():
    payload = PartnerServiceListRequestedPayload()

    assert PartnerServiceListRequestedPayload.model_validate_json(payload.model_dump_json()) == payload
