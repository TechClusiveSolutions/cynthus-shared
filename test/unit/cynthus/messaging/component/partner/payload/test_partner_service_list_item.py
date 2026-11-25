"""Tests for cynthus.messaging.component.partner.payload.partner_service_list_item."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.messaging.component.partner.payload.partner_service_list_item import PartnerServiceListItem


def test_an_item_has_an_id_and_a_name():
    item_id = uuid4()
    item = PartnerServiceListItem(id=item_id, name='Acme')

    assert (item.id, item.name) == (item_id, 'Acme')


def test_an_item_accepts_a_uuid_string():
    item_id = uuid4()

    assert PartnerServiceListItem(id=str(item_id), name='Acme').id == item_id


@pytest.mark.parametrize('kwargs', [{'name': 'Acme'}, {'id': uuid4()}, {}])
def test_an_item_requires_id_and_name(kwargs):
    with pytest.raises(ValidationError):
        PartnerServiceListItem(**kwargs)


@pytest.mark.parametrize('item_id', ['not-a-uuid', 5, None, ''])
def test_an_item_rejects_a_bad_id(item_id):
    with pytest.raises(ValidationError):
        PartnerServiceListItem(id=item_id, name='Acme')


@pytest.mark.parametrize('name', [5, None, ['a']])
def test_an_item_rejects_a_non_string_name(name):
    with pytest.raises(ValidationError):
        PartnerServiceListItem(id=uuid4(), name=name)
