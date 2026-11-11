import pytest

from cynthus.security import AccessRecorder, TokenClaims


@pytest.mark.asyncio
async def test_the_default_recorder_accepts_every_decision_and_does_nothing(identity):
    claims = TokenClaims(**identity, issued_at=1, expires_at=2)
    recorder = AccessRecorder()

    assert await recorder.granted(claims, 'inventory:read', '/x', 'GET') is None
    assert await recorder.rejected('invalid token', '/x', 'GET') is None
    assert await recorder.denied(claims, 'inventory:read', '/x', 'GET') is None
