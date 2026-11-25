"""Tests for cynthus.messaging.test.factory.partner.message.service_list_requested_message (PartnerServiceListRequestedMessageFactory)."""

from uuid import UUID, uuid4

import pytest

from cynthus.messaging.common.signal import LifecycleAction, PublicPartnerServiceListRequestedSignal
from cynthus.messaging.component.partner.message import PartnerServiceListRequestedMessage
from cynthus.messaging.test.factory.partner.message.service_list_requested_message import (
    PartnerServiceListRequestedMessageFactory,
)


@pytest.fixture(scope='module')
def factory():
    return PartnerServiceListRequestedMessageFactory


def test_builds_the_matching_message_type(factory):
    assert isinstance(factory(), PartnerServiceListRequestedMessage)


def test_event_type_is_the_signal_name(factory):
    assert factory().event_type == PublicPartnerServiceListRequestedSignal.name


def test_lifecycle_action(factory):
    assert factory().lifecycle_action == LifecycleAction.CREATED


def test_envelope_identifiers_are_uuids_and_fresh_for_every_message(factory):
    first, second = factory(), factory()

    for name in ('correlation_id', 'actor_id', 'organization_id', 'workspace_id', 'event_id'):
        assert isinstance(getattr(first, name), UUID)
        assert getattr(first, name) != getattr(second, name)


def test_payload_defaults(factory):
    assert factory().payload.schema_version == 1
    assert factory().payload.filters.name is None


def test_envelope_values_can_be_overridden(factory):
    identifier = uuid4()

    assert factory(actor_id=identifier).actor_id == identifier


def test_payload_values_can_be_overridden(factory):
    assert factory(payload__filters={'name': 'acme'}).payload.filters.name == 'acme'
