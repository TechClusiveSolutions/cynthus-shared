"""Tests for cynthus.core.event.partner_service_list_responded_data (PartnerServiceListRespondedData)."""

from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from cynthus.core.event.partner_service_list_item_data import PartnerServiceListItemData
from cynthus.core.event.partner_service_list_responded_data import PartnerServiceListRespondedData


def test_is_a_pydantic_model():
    assert issubclass(PartnerServiceListRespondedData, BaseModel)


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.PartnerServiceListRespondedData is PartnerServiceListRespondedData


def test_fields_are_exactly_the_contract():
    assert set(PartnerServiceListRespondedData.model_fields) == {'schema_version', 'status', 'result', 'error'}


def test_defaults():
    data = PartnerServiceListRespondedData(status=200)

    assert data.schema_version == 1
    assert data.status == 200
    assert data.result is None
    assert data.error is None


def test_status_is_required():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedData()


def test_status_must_be_an_integer():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedData(status='ok')


def test_items_are_parsed_from_dicts():
    first, second = uuid4(), uuid4()
    data = PartnerServiceListRespondedData.model_validate({
        'status': 200,
        'result': [{'id': str(first), 'name': 'A'}, {'id': str(second), 'name': 'B'}],
    })

    assert all(isinstance(item, PartnerServiceListItemData) for item in data.result)
    assert [(item.id, item.name) for item in data.result] == [(first, 'A'), (second, 'B')]


def test_empty_result_is_not_none():
    assert PartnerServiceListRespondedData(status=200, result=[]).result == []


def test_error_is_kept():
    data = PartnerServiceListRespondedData(status=422, error='bad filter')

    assert data.error == 'bad filter'
    assert data.result is None


def test_error_must_be_a_string():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedData(status=422, error=5)


def test_item_with_an_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedData.model_validate({'status': 200, 'result': [{'id': str(uuid4()), 'name': 'A', 'x': 1}]})


def test_item_with_a_bad_id_is_refused():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedData.model_validate({'status': 200, 'result': [{'id': 'nope', 'name': 'A'}]})


@pytest.mark.parametrize('bad', [0, -1])
def test_schema_version_must_be_at_least_one(bad):
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedData(status=200, schema_version=bad)


def test_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        PartnerServiceListRespondedData.model_validate({'status': 200, 'other': 1})


def test_extra_is_forbidden_in_the_config():
    assert PartnerServiceListRespondedData.model_config['extra'] == 'forbid'
