"""Tests for cynthus.core.event.partner_service_list_responded_event (PartnerServiceListRespondedEvent)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.core.event import EventAction, PartnerEvent, PartnerServiceListRequestedEvent
from cynthus.core.event.partner_service_list_responded_data import PartnerServiceListRespondedData
from cynthus.core.event.partner_service_list_responded_event import PartnerServiceListRespondedEvent as Direct


def _ids():
    return {'tenant_id': uuid4(), 'workspace_id': uuid4(), 'actor_id': uuid4()}


def _make(data, action=EventAction.RETRIEVED):
    return Direct(**_ids(), action=action, data=data)


def _request(service_id=None):
    return PartnerServiceListRequestedEvent(
        **_ids(), service_id=service_id, action=EventAction.RETRIEVED, data={'filters': {'name': 'x'}},
    )


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.PartnerServiceListRespondedEvent is Direct


def test_is_a_partner_event():
    assert issubclass(Direct, PartnerEvent)


def test_declares_its_data_model_and_actions():
    assert Direct.data_model is PartnerServiceListRespondedData
    assert Direct.actions == frozenset({EventAction.RETRIEVED})


def test_event_type():
    assert _make({'status': 200}).event_type == 'partner_service_list_responded'


class TestValidation:
    def test_status_only(self):
        parsed = _make({'status': 200}).parsed_data(PartnerServiceListRespondedData)

        assert (parsed.schema_version, parsed.status, parsed.result, parsed.error) == (1, 200, None, None)

    def test_status_is_required(self):
        with pytest.raises(ValidationError):
            _make({})

    def test_non_integer_status_is_refused(self):
        with pytest.raises(ValidationError):
            _make({'status': 'ok'})

    def test_items_are_accepted(self):
        first, second = uuid4(), uuid4()
        parsed = _make({
            'status': 200, 'result': [{'id': str(first), 'name': 'A'}, {'id': str(second), 'name': 'B'}],
        }).parsed_data(PartnerServiceListRespondedData)

        assert [(i.id, i.name) for i in parsed.result] == [(first, 'A'), (second, 'B')]

    def test_item_with_a_bad_id_is_refused(self):
        with pytest.raises(ValidationError):
            _make({'status': 200, 'result': [{'id': 'nope', 'name': 'A'}]})

    def test_item_with_a_missing_name_is_refused(self):
        with pytest.raises(ValidationError):
            _make({'status': 200, 'result': [{'id': str(uuid4())}]})

    def test_error_is_accepted(self):
        assert _make({'status': 403, 'error': 'no'}).parsed_data(PartnerServiceListRespondedData).error == 'no'

    def test_non_string_error_is_refused(self):
        with pytest.raises(ValidationError):
            _make({'status': 403, 'error': 5})

    def test_unknown_key_is_refused(self):
        with pytest.raises(ValidationError):
            _make({'status': 200, 'other': 1})

    @pytest.mark.parametrize('action', [a for a in EventAction if a != EventAction.RETRIEVED])
    def test_any_other_action_is_refused(self, action):
        with pytest.raises(ValidationError):
            _make({'status': 200}, action=action)


class TestAnswering:
    def test_is_a_classmethod(self):
        assert isinstance(Direct.__dict__['answering'], classmethod)

    def test_copies_the_ids_from_the_request(self):
        request = _request(service_id=uuid4())

        response = Direct.answering(request, status=200)

        assert type(response) is Direct
        assert response.correlation_id == request.correlation_id
        assert response.tenant_id == request.tenant_id
        assert response.workspace_id == request.workspace_id
        assert response.actor_id == request.actor_id
        assert response.service_id == request.service_id

    def test_service_id_none_is_copied(self):
        assert Direct.answering(_request(), status=200).service_id is None

    def test_has_a_new_id_and_a_fresh_time(self):
        request = _request()
        before = datetime.now(timezone.utc)

        response = Direct.answering(request, status=200)

        assert response.id_ != request.id_
        assert response.occurred_on >= before
        assert response.occurred_on <= datetime.now(timezone.utc)
        assert Direct.answering(request, status=200).id_ != response.id_

    def test_action_is_retrieved(self):
        assert Direct.answering(_request(), status=200).action == EventAction.RETRIEVED

    def test_items_become_id_and_name(self):
        first, second = uuid4(), uuid4()

        response = Direct.answering(_request(), status=200, items=[(first, 'A'), (second, 'B')])

        assert response.data['status'] == 200
        assert response.data['result'] == [{'id': str(first), 'name': 'A'}, {'id': str(second), 'name': 'B'}]
        parsed = response.parsed_data(PartnerServiceListRespondedData).result
        assert [(i.id, i.name) for i in parsed] == [(first, 'A'), (second, 'B')]
        assert response.data['error'] is None
        assert response.data['schema_version'] == 1

    def test_no_items_gives_result_none(self):
        response = Direct.answering(_request(), status=200)

        assert response.data['result'] is None
        assert response.parsed_data(PartnerServiceListRespondedData).result is None

    def test_empty_items_give_an_empty_list(self):
        response = Direct.answering(_request(), status=200, items=[])

        assert response.parsed_data(PartnerServiceListRespondedData).result == []

    def test_error_is_set(self):
        response = Direct.answering(_request(), status=422, error='bad filter')

        assert response.data['error'] == 'bad filter'
        assert response.data['status'] == 422
        assert response.data['result'] is None

    def test_data_validates_against_the_data_model(self):
        item = uuid4()

        parsed = Direct.answering(_request(), status=200, items=((item, 'A'),)).parsed_data(PartnerServiceListRespondedData)

        assert parsed.result[0].id == item
        assert parsed.result[0].name == 'A'

    def test_the_request_is_not_changed(self):
        request = _request()
        snapshot = request.model_dump()

        Direct.answering(request, status=200)

        assert request.model_dump() == snapshot

    def test_data_is_complete(self):
        response = Direct.answering(_request(), status=200)

        assert response.data == {'schema_version': 1, 'status': 200, 'result': None, 'error': None}

    def test_invalid_status_type_is_refused(self):
        with pytest.raises(ValidationError):
            Direct.answering(_request(), status='ok')

    def test_invalid_item_is_refused(self):
        with pytest.raises(ValidationError):
            Direct.answering(_request(), status=200, items=[('nope', 'A')])
