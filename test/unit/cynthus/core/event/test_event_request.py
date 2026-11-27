"""EventRequest class unit tests for the Cynthus project"""

from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from cynthus.core.event import EventAction, EventRequest, SignalEvent
from cynthus.core.system import System
from cynthus.core.test.factory import EventRequestFactory, UserEventFactory, UserFactory


def _signal_event():
    return SignalEvent(tenant_id=uuid4(), workspace_id=uuid4(), actor_id=uuid4(), action=EventAction.RETRIEVED, data={})


def test_a_request_for_a_full_event_and_a_user_is_unchanged():
    request = EventRequestFactory()

    assert request.requestor_id == request.requestor.id_
    assert request.event is not None and request.reason is None and request.in_reply_to is None


def test_a_request_accepts_a_signal_event_and_a_uuid_requestor():
    event, requestor = _signal_event(), uuid4()

    request = EventRequest(event=event, requestor=requestor)

    assert request.event == event
    assert request.requestor == requestor


def test_the_requestor_id_of_a_user_is_the_user_id():
    user = UserFactory()

    assert EventRequest(event=UserEventFactory(), requestor=user).requestor_id == user.id_


def test_the_requestor_id_of_a_system_is_the_system_id():
    system = System()

    request = EventRequest(event=UserEventFactory(), requestor=system)

    assert request.requestor_id == system.id_
    assert isinstance(request.requestor_id, UUID)


def test_the_requestor_id_of_a_uuid_is_that_uuid():
    requestor = uuid4()

    assert EventRequest(event=_signal_event(), requestor=requestor).requestor_id == requestor


def test_a_signal_event_request_may_have_a_user_requestor():
    user = UserFactory()

    assert EventRequest(event=_signal_event(), requestor=user).requestor_id == user.id_


def test_a_uuid_given_as_text_is_read_as_the_requestor_id():
    requestor = uuid4()

    request = EventRequest(event=_signal_event(), requestor=str(requestor))

    assert request.requestor_id == requestor


@pytest.mark.parametrize('requestor', [None, 0, '', 'not-a-uuid', 12, []])
def test_a_requestor_that_is_not_a_user_system_or_uuid_is_refused(requestor):
    with pytest.raises(ValidationError):
        EventRequest(event=_signal_event(), requestor=requestor)


@pytest.mark.parametrize('event', [None, {}, '', 0, 'event'])
def test_an_event_that_is_neither_an_event_nor_a_signal_event_is_refused(event):
    with pytest.raises(ValidationError):
        EventRequest(event=event, requestor=uuid4())


def test_the_defaults_still_apply_to_a_signal_request():
    first = EventRequest(event=_signal_event(), requestor=uuid4())
    second = EventRequest(event=_signal_event(), requestor=uuid4())

    assert first.id_ != second.id_
    assert first.requested_on.tzinfo is not None
    assert first.reason is None and first.in_reply_to is None
