"""Tests for cynthus.messaging.component.identity.message.identity_email_verified."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.identity import IdentityEmailVerifiedMessage as ExportedMessage
from cynthus.messaging.component.identity import IdentityEmailVerifiedPayload as ExportedPayload
from cynthus.messaging.component.identity.message.identity_email_verified import IdentityEmailVerifiedMessage
from cynthus.messaging.component.identity.payload.identity_email_verified import IdentityEmailVerifiedPayload


def make_message():
    return IdentityEmailVerifiedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=IdentityEmailVerifiedPayload(user_id='u1', username='ada@example.com'),
    )


def test_event_type():
    assert make_message().event_type == 'audit.identity.email.verified'


def test_round_trips_through_json():
    message = make_message()

    assert IdentityEmailVerifiedMessage.model_validate_json(message.model_dump_json()) == message


def test_it_is_exported_from_the_identity_package():
    assert ExportedMessage is IdentityEmailVerifiedMessage
    assert ExportedPayload is IdentityEmailVerifiedPayload


def test_the_serialised_message_holds_no_secret_field():
    text = make_message().model_dump_json().lower()

    assert 'password' not in text and 'token' not in text and 'hash' not in text
