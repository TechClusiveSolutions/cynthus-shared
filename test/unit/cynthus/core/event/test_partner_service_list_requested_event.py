"""Tests for cynthus.core.event.partner_service_list_requested_event (PartnerServiceListRequestedEvent)."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.core.event import EventAction, PartnerEvent, SignalEvent
from cynthus.core.event.partner_service_list_filters_data import PartnerServiceListFiltersData
from cynthus.core.event.partner_service_list_requested_data import PartnerServiceListRequestedData
from cynthus.core.event.partner_service_list_requested_event import PartnerServiceListRequestedEvent as Direct


def _make(data=None, action=EventAction.RETRIEVED):
    return Direct(
        tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=action,
        data={} if data is None else data,
    )


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.PartnerServiceListRequestedEvent is Direct


def test_is_a_partner_event():
    assert issubclass(Direct, PartnerEvent)
    assert issubclass(Direct, SignalEvent)


def test_declares_its_data_model_and_actions():
    assert Direct.data_model is PartnerServiceListRequestedData
    assert Direct.actions == frozenset({EventAction.RETRIEVED})


def test_event_type():
    assert _make().event_type == 'partner_service_list_requested'


def test_no_data_gives_the_defaults():
    parsed = _make({}).parsed_data(PartnerServiceListRequestedData)

    assert parsed.schema_version == 1
    assert parsed.filters == PartnerServiceListFiltersData()


def test_name_filter_is_accepted():
    parsed = _make({'filters': {'name': 'Butcher'}}).parsed_data(PartnerServiceListRequestedData)

    assert parsed.filters.name == 'Butcher'


def test_schema_version_is_accepted():
    assert _make({'schema_version': 2}).parsed_data(PartnerServiceListRequestedData).schema_version == 2


def test_unknown_key_is_refused():
    with pytest.raises(ValidationError):
        _make({'other': 1})


def test_unknown_filter_key_is_refused():
    with pytest.raises(ValidationError):
        _make({'filters': {'other': 1}})


@pytest.mark.parametrize('bad', [5, ['a'], True])
def test_non_string_name_is_refused(bad):
    with pytest.raises(ValidationError):
        _make({'filters': {'name': bad}})


@pytest.mark.parametrize('action', [a for a in EventAction if a != EventAction.RETRIEVED])
def test_any_other_action_is_refused(action):
    with pytest.raises(ValidationError):
        _make({}, action=action)


def test_model_copy_validates_again():
    event = _make({'filters': {'name': 'A'}})

    with pytest.raises(ValidationError):
        event.model_copy(update={'data': {'other': 1}})
