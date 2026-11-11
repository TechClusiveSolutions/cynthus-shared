"""Tests for cynthus.messaging.component.identity.message.identity_user_registered."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.identity import IdentityUserRegisteredMessage as ExportedMessage
from cynthus.messaging.component.identity import IdentityUserRegisteredPayload as ExportedPayload
from cynthus.messaging.component.identity.message.identity_user_registered import IdentityUserRegisteredMessage
from cynthus.messaging.component.identity.payload.identity_user_registered import IdentityUserRegisteredPayload


def make_message():
    return IdentityUserRegisteredMessage(
        lifecycle_action=LifecycleAction.CREATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=IdentityUserRegisteredPayload(user_id='u1', username='ada@example.com'),
    )


def test_event_type():
    assert make_message().event_type == 'audit.identity.user.registered'


def test_round_trips_through_json():
    message = make_message()

    assert IdentityUserRegisteredMessage.model_validate_json(message.model_dump_json()) == message


def test_it_is_exported_from_the_identity_package():
    assert ExportedMessage is IdentityUserRegisteredMessage
    assert ExportedPayload is IdentityUserRegisteredPayload


def test_the_serialised_message_holds_no_secret_field():
    text = make_message().model_dump_json().lower()

    assert 'password' not in text and 'token' not in text and 'hash' not in text
