"""Tests for cynthus.messaging.component.partner.payload.partner_service_list_filters."""

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.partner.payload.partner_service_list_filters import PartnerServiceListFilters


def test_filters_default_to_no_name():
    assert PartnerServiceListFilters().name is None


def test_filters_accept_a_name():
    assert PartnerServiceListFilters(name='acme').name == 'acme'


def test_filters_accept_an_empty_string():
    assert PartnerServiceListFilters(name='').name == ''


@pytest.mark.parametrize('name', [1, 1.5, True, ['acme'], {'a': 1}])
def test_filters_reject_a_non_string_name(name):
    with pytest.raises(ValidationError):
        PartnerServiceListFilters(name=name)


def test_filters_reject_an_unknown_key():
    with pytest.raises(ValidationError):
        PartnerServiceListFilters(colour='red')


def test_filters_reject_an_unknown_key_beside_a_valid_one():
    with pytest.raises(ValidationError):
        PartnerServiceListFilters(name='acme', colour='red')
