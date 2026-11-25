"""Tests for cynthus.core.event.partner_event (PartnerEvent)."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from cynthus.core.event import EventAction, SignalEvent
from cynthus.core.event.partner_event import PartnerEvent


def _ids():
    return {'tenant_id': uuid4(), 'workspace_id': uuid4(), 'actor_id': uuid4()}


def test_is_exported_from_the_package():
    import cynthus.core.event as package

    assert package.PartnerEvent is PartnerEvent


def test_is_a_signal_event():
    assert issubclass(PartnerEvent, SignalEvent)


def test_allows_only_retrieved():
    assert PartnerEvent.actions == frozenset({EventAction.RETRIEVED})


def test_retrieved_is_accepted():
    event = PartnerEvent(**_ids(), action=EventAction.RETRIEVED, data={})

    assert event.action == EventAction.RETRIEVED


@pytest.mark.parametrize('action', [a for a in EventAction if a != EventAction.RETRIEVED])
def test_any_other_action_is_refused(action):
    with pytest.raises(ValidationError):
        PartnerEvent(**_ids(), action=action, data={})
