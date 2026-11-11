from uuid import UUID

import pytest

from cynthus.security import SignalAccessRecorder, TokenClaims


class FakePublisher:
    def __init__(self):
        self.messages = []

    async def publish(self, message, access_token=None):
        self.messages.append(message)


def _claims(identity, permissions=('inventory:read',)):
    return TokenClaims(
        **identity, token_id='jti-1', roles=['team_member'], permissions=list(permissions), issued_at=1, expires_at=2
    )


@pytest.mark.asyncio
async def test_a_granted_request_is_published_with_the_callers_tenant(identity):
    publisher = FakePublisher()

    await SignalAccessRecorder(publisher).granted(_claims(identity), 'inventory:read', '/api/v1/x', 'GET')

    (message,) = publisher.messages
    assert message.event_type == 'audit.identity.access.granted'
    assert message.payload.user_id == str(identity['subject']) and message.payload.token_id == 'jti-1'
    assert (message.payload.permission, message.payload.resource, message.payload.method) == (
        'inventory:read', '/api/v1/x', 'GET')
    assert (message.organization_id, message.workspace_id, message.actor_id) == (
        identity['organization_id'], identity['workspace_id'], identity['subject'])


@pytest.mark.asyncio
async def test_a_rejected_request_is_published_without_a_tenant(identity):
    publisher = FakePublisher()

    await SignalAccessRecorder(publisher).rejected('token expired', '/api/v1/x', 'POST')

    (message,) = publisher.messages
    assert message.event_type == 'audit.identity.access.rejected'
    assert (message.payload.reason, message.payload.resource, message.payload.method) == (
        'token expired', '/api/v1/x', 'POST')
    assert (message.organization_id, message.workspace_id, message.actor_id) == (UUID(int=0),) * 3


@pytest.mark.asyncio
async def test_a_denied_request_names_the_permission_the_roles_and_what_the_token_had(identity):
    publisher = FakePublisher()

    await SignalAccessRecorder(publisher).denied(
        _claims(identity, permissions=['inventory:read']), 'inventory:write', '/api/v1/x', 'DELETE'
    )

    (message,) = publisher.messages
    assert message.event_type == 'audit.identity.access.denied'
    assert message.payload.required_permission == 'inventory:write'
    assert message.payload.granted_permissions == ['inventory:read']
    assert message.payload.roles == ['team_member']
    assert message.payload.user_id == str(identity['subject'])
    assert (message.organization_id, message.actor_id) == (identity['organization_id'], identity['subject'])


@pytest.mark.asyncio
async def test_every_signal_gets_its_own_correlation_id(identity):
    publisher = FakePublisher()
    recorder = SignalAccessRecorder(publisher)

    await recorder.granted(_claims(identity), 'inventory:read', '/a', 'GET')
    await recorder.granted(_claims(identity), 'inventory:read', '/a', 'GET')

    assert publisher.messages[0].correlation_id != publisher.messages[1].correlation_id
