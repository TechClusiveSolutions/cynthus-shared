"""Tests for PartnerServiceListRequestedMessage."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.messaging.common import LifecycleAction, PublicPartnerServiceListRequestedSignal
from cynthus.messaging.component.partner import PartnerServiceListRequestedMessage, PartnerServiceListRequestedPayload


def make_message(**payload_kwargs):
    return PartnerServiceListRequestedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=PartnerServiceListRequestedPayload(**payload_kwargs),
    )


def test_event_type():
    assert make_message().event_type == 'public.partner.service_list.requested'


def test_event_type_equals_the_signal_name():
    assert make_message().event_type == PublicPartnerServiceListRequestedSignal.name


def test_payload_is_typed():
    assert isinstance(make_message().payload, PartnerServiceListRequestedPayload)


def test_the_payload_is_required():
    with pytest.raises(ValidationError):
        PartnerServiceListRequestedMessage(
            lifecycle_action=LifecycleAction.UPDATED,
            correlation_id=uuid4(),
            organization_id=uuid4(),
            workspace_id=uuid4(),
            actor_id=uuid4(),
        )


def test_round_trips_through_json():
    message = make_message(filters={'name': 'acme'})

    restored = PartnerServiceListRequestedMessage.model_validate_json(message.model_dump_json())

    assert restored == message
    assert restored.correlation_id == message.correlation_id
    assert restored.organization_id == message.organization_id
    assert restored.workspace_id == message.workspace_id
    assert restored.actor_id == message.actor_id
    assert restored.payload.filters.name == 'acme'


def test_round_trips_with_default_filters():
    message = make_message()

    assert PartnerServiceListRequestedMessage.model_validate_json(message.model_dump_json()) == message
