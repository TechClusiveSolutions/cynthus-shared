"""tenant_id beside organization_id on signal messages (ADR-010): one value, either name, both written."""

import json
import uuid

import pytest
from pydantic import ValidationError

from cynthus.messaging.common.signal import LifecycleAction
from cynthus.messaging.common.signal.message_base import SignalMessageBase


def fields(**extra):
    return {
        'event_type': 'public.test.thing.created', 'lifecycle_action': LifecycleAction.CREATED,
        'correlation_id': uuid.uuid4(), 'workspace_id': uuid.uuid4(), 'actor_id': uuid.uuid4(), **extra,
    }


def test_a_signal_with_only_the_organization_id_gets_the_same_tenant_id():
    tenant = uuid.uuid4()

    message = SignalMessageBase(**fields(organization_id=tenant))

    assert message.tenant_id == message.organization_id == tenant


def test_a_signal_with_only_the_tenant_id_gets_the_same_organization_id():
    tenant = uuid.uuid4()

    message = SignalMessageBase(**fields(tenant_id=tenant))

    assert message.organization_id == message.tenant_id == tenant


def test_a_signal_with_both_names_for_one_tenant_is_accepted():
    tenant = uuid.uuid4()

    message = SignalMessageBase(**fields(organization_id=tenant, tenant_id=str(tenant)))

    assert message.tenant_id == message.organization_id == tenant


def test_a_signal_with_two_different_tenants_is_refused():
    with pytest.raises(ValidationError, match='one value; they differ'):
        SignalMessageBase(**fields(organization_id=uuid.uuid4(), tenant_id=uuid.uuid4()))


def test_a_signal_with_neither_is_refused():
    with pytest.raises(ValidationError):
        SignalMessageBase(**fields())


def test_both_names_are_written_to_the_json():
    tenant = uuid.uuid4()

    written = json.loads(SignalMessageBase(**fields(tenant_id=tenant)).model_dump_json())

    assert written['tenant_id'] == written['organization_id'] == str(tenant)


def test_json_from_a_publisher_that_knows_only_the_organization_id_still_reads():
    tenant = uuid.uuid4()
    old = json.loads(SignalMessageBase(**fields(organization_id=tenant)).model_dump_json())
    del old['tenant_id']

    read = SignalMessageBase.model_validate_json(json.dumps(old))

    assert read.tenant_id == tenant


def test_json_from_a_publisher_that_knows_only_the_tenant_id_reads_too():
    tenant = uuid.uuid4()
    new = json.loads(SignalMessageBase(**fields(tenant_id=tenant)).model_dump_json())
    del new['organization_id']

    assert SignalMessageBase.model_validate_json(json.dumps(new)).organization_id == tenant
