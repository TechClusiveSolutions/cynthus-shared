"""Tests for cynthus.core.event.partner_service_list_requested_data (PartnerServiceListRequestedData)."""

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.partner_service_list_filters_data import PartnerServiceListFiltersData
from cynthus.core.event.partner_service_list_requested_data import PartnerServiceListRequestedData


def test_is_a_pydantic_model():
    assert issubclass(PartnerServiceListRequestedData, BaseModel)


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.PartnerServiceListRequestedData is PartnerServiceListRequestedData


def test_fields_are_exactly_the_contract():
    assert set(PartnerServiceListRequestedData.model_fields) == {'schema_version', 'filters'}


def test_defaults():
    data = PartnerServiceListRequestedData()

    assert data.schema_version == 1
    assert data.filters == PartnerServiceListFiltersData()
    assert data.filters.name is None


def test_default_filters_are_not_shared():
    assert PartnerServiceListRequestedData().filters is not PartnerServiceListRequestedData().filters


def test_filters_are_parsed_from_a_dict():
    data = PartnerServiceListRequestedData.model_validate({'filters': {'name': 'Butcher'}})

    assert isinstance(data.filters, PartnerServiceListFiltersData)
    assert data.filters.name == 'Butcher'


def test_schema_version_is_kept():
    assert PartnerServiceListRequestedData(schema_version=3).schema_version == 3


@pytest.mark.parametrize('bad', [0, -1])
def test_schema_version_must_be_at_least_one(bad):
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedData(schema_version=bad)


def test_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedData.model_validate({'other': 1})


def test_unknown_filter_key_is_refused():
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedData.model_validate({'filters': {'other': 1}})


def test_extra_is_forbidden_in_the_config():
    assert PartnerServiceListRequestedData.model_config['extra'] == 'forbid'
