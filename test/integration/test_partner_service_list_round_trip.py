"""Feature integration (AC4e): a real partner event goes through ``EventMessagePublisher`` with a recording transport,
to JSON text, to a message, to ``SignalEventReader.read``, and comes back as an equal event."""

from uuid import uuid4

import pytest

from cynthus.core.event import (
    EventAction,
    PartnerServiceListRequestedData,
    PartnerServiceListRequestedEvent,
    PartnerServiceListRespondedData,
    PartnerServiceListRespondedEvent,
)
from cynthus.messaging.generator import SignalEventReader
from cynthus.messaging.publisher.event_message_publisher import EventMessagePublisher
from cynthus.messaging.publisher.signal_publisher import SignalPublisher
from cynthus.security import TokenClaims


class _Recording(SignalPublisher):
    def __init__(self):
        self.calls = []

    async def publish(self, message, access_token=None, *, topic=None):
        self.calls.append((message, access_token, topic))


def _ids():
    return {'tenant_id': uuid4(), 'workspace_id': uuid4(), 'actor_id': uuid4()}


def _requested(data=None):
    return PartnerServiceListRequestedEvent(**_ids(), action=EventAction.RETRIEVED, data={} if data is None else data)


def _responded(data):
    return PartnerServiceListRespondedEvent(**_ids(), action=EventAction.RETRIEVED, data=data)


def _claims(event):
    return TokenClaims(
        subject=event.actor_id, organization_id=event.tenant_id, workspace_id=event.workspace_id,
        issued_at=1_000, expires_at=2_000,
    )


@pytest.mark.asyncio
class TestPartnerServiceListRoundTrip:
    async def _round_trip(self, event):
        transport = _Recording()

        await EventMessagePublisher(transport).publish(event, 'token')

        assert len(transport.calls) == 1
        message = transport.calls[0][0]
        text = message.model_dump_json()
        received = type(message).model_validate_json(text)
        read = SignalEventReader().read(received, _claims(event), type(event))

        assert type(read) is type(event)
        assert read.id_ == event.id_
        assert read.correlation_id == event.correlation_id
        assert read.occurred_on == event.occurred_on
        assert read.tenant_id == event.tenant_id
        assert read.workspace_id == event.workspace_id
        assert read.actor_id == event.actor_id
        assert read.action == EventAction.RETRIEVED
        assert read.data == event.parsed_data(type(event).data_model).model_dump(mode='json')

        return read

    async def test_requested_event(self):
        event = _requested({'schema_version': 1, 'filters': {'name': 'Butcher'}})

        read = await self._round_trip(event)

        assert read.data == event.data
        assert read.parsed_data(PartnerServiceListRequestedData) == event.parsed_data(PartnerServiceListRequestedData)
        assert read.parsed_data(PartnerServiceListRequestedData).filters.name == 'Butcher'

    async def test_requested_event_without_data(self):
        event = _requested()

        read = await self._round_trip(event)

        assert read.data == {'schema_version': 1, 'filters': {'name': None}}

        assert read.parsed_data(PartnerServiceListRequestedData) == event.parsed_data(PartnerServiceListRequestedData)

    async def test_responded_event_with_two_items(self):
        first, second = uuid4(), uuid4()
        event = _responded({
            'schema_version': 1, 'status': 200, 'error': None,
            'result': [{'id': str(first), 'name': 'A'}, {'id': str(second), 'name': 'B'}],
        })

        read = await self._round_trip(event)

        assert read.data == event.data
        parsed = read.parsed_data(PartnerServiceListRespondedData)
        assert parsed == event.parsed_data(PartnerServiceListRespondedData)
        assert [(item.id, item.name) for item in parsed.result] == [(first, 'A'), (second, 'B')]

    async def test_responded_event_with_an_error(self):
        event = _responded({'schema_version': 1, 'status': 422, 'result': None, 'error': 'bad filter'})

        read = await self._round_trip(event)

        assert read.data == event.data
        parsed = read.parsed_data(PartnerServiceListRespondedData)
        assert parsed == event.parsed_data(PartnerServiceListRespondedData)
        assert (parsed.status, parsed.error, parsed.result) == (422, 'bad filter', None)

    async def test_answering_event(self):
        request = _requested()
        response = PartnerServiceListRespondedEvent.answering(request, status=200, items=[(uuid4(), 'A')])

        read = await self._round_trip(response)

        assert read.correlation_id == request.correlation_id
        assert read.data == response.data
        parsed = read.parsed_data(PartnerServiceListRespondedData)
        assert parsed == response.parsed_data(PartnerServiceListRespondedData)
