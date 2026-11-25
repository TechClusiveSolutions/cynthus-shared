"""Tests for cynthus.messaging.test.factory.partner.message.service_list_responded_payload (PartnerServiceListRespondedPayloadFactory)."""

from cynthus.messaging.component.partner.payload import PartnerServiceListRespondedPayload
from cynthus.messaging.test.factory.partner.message.service_list_responded_payload import (
    PartnerServiceListRespondedPayloadFactory,
)


def test_builds_the_matching_payload_type():
    assert isinstance(PartnerServiceListRespondedPayloadFactory(), PartnerServiceListRespondedPayload)


def test_schema_version_defaults_to_1():
    assert PartnerServiceListRespondedPayloadFactory().schema_version == 1


def test_status_defaults_to_200():
    assert PartnerServiceListRespondedPayloadFactory().status == 200


def test_status_can_be_overridden():
    assert PartnerServiceListRespondedPayloadFactory(status=422).status == 422
