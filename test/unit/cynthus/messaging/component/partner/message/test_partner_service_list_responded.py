"""Tests for PartnerServiceListRespondedMessage."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.messaging.common import LifecycleAction, PublicPartnerServiceListRespondedSignal
from cynthus.messaging.component.partner import (
    PartnerServiceListItem,
    PartnerServiceListRespondedMessage,
    PartnerServiceListRespondedPayload,
)


def make_message(**payload_kwargs):
    return PartnerServiceListRespondedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=PartnerServiceListRespondedPayload(**payload_kwargs),
    )


def test_event_type():
    assert make_message(status=200).event_type == 'public.partner.service_list.responded'


def test_event_type_equals_the_signal_name():
    assert make_message(status=200).event_type == PublicPartnerServiceListRespondedSignal.name


def test_payload_is_typed():
    assert isinstance(make_message(status=200).payload, PartnerServiceListRespondedPayload)


def test_an_invalid_payload_status_is_rejected():
    with pytest.raises(ValidationError):
        make_message(status='ok')


def test_round_trips_with_a_result():
    items = [PartnerServiceListItem(id=uuid4(), name='A'), PartnerServiceListItem(id=uuid4(), name='B')]
    message = make_message(status=200, result=items)

    restored = PartnerServiceListRespondedMessage.model_validate_json(message.model_dump_json())

    assert restored == message
    assert restored.correlation_id == message.correlation_id
    assert restored.organization_id == message.organization_id
    assert restored.workspace_id == message.workspace_id
    assert restored.actor_id == message.actor_id
    assert [item.name for item in restored.payload.result] == ['A', 'B']


def test_round_trips_with_an_error():
    message = make_message(status=422, error='bad filter')

    restored = PartnerServiceListRespondedMessage.model_validate_json(message.model_dump_json())

    assert restored == message
    assert restored.payload.result is None
    assert restored.payload.error == 'bad filter'
