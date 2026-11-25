"""Tests for cynthus.messaging.test.factory.partner.message.service_list_requested_payload (PartnerServiceListRequestedPayloadFactory)."""

from cynthus.messaging.component.partner.payload import PartnerServiceListRequestedPayload
from cynthus.messaging.test.factory.partner.message.service_list_requested_payload import (
    PartnerServiceListRequestedPayloadFactory,
)


def test_builds_the_matching_payload_type():
    assert isinstance(PartnerServiceListRequestedPayloadFactory(), PartnerServiceListRequestedPayload)


def test_schema_version_defaults_to_1():
    assert PartnerServiceListRequestedPayloadFactory().schema_version == 1


def test_filters_can_be_overridden():
    assert PartnerServiceListRequestedPayloadFactory(filters={'name': 'acme'}).filters.name == 'acme'
