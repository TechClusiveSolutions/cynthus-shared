"""Tests for cynthus.core.event.partner_service_list_filters_data (PartnerServiceListFiltersData)."""

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.partner_service_list_filters_data import PartnerServiceListFiltersData


def test_is_a_pydantic_model():
    assert issubclass(PartnerServiceListFiltersData, BaseModel)


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.PartnerServiceListFiltersData is PartnerServiceListFiltersData


def test_fields_are_exactly_the_contract():
    assert set(PartnerServiceListFiltersData.model_fields) == {'name'}


def test_name_defaults_to_none():
    assert PartnerServiceListFiltersData().name is None


def test_name_is_kept():
    assert PartnerServiceListFiltersData(name='Butcher').name == 'Butcher'


@pytest.mark.parametrize('bad', [5, ['a'], {'a': 1}])
def test_name_must_be_a_string(bad):
    with pytest.raises(ValidationError):
        PartnerServiceListFiltersData(name=bad)


def test_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        PartnerServiceListFiltersData(name='x', other=1)


def test_extra_is_forbidden_in_the_config():
    assert PartnerServiceListFiltersData.model_config['extra'] == 'forbid'
