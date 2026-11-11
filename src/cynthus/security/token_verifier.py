"""Access token verifier for the Cynthus project"""

import asyncio
from os import environ
from typing import Any

import jwt
from pydantic import ValidationError

from .token_claims import TokenClaims
from .token_error import TokenError

ALGORITHM = 'RS256'
DEFAULT_ISSUER = 'cynthus-auth'
DEFAULT_AUDIENCE = 'cynthus'
DEFAULT_JWKS_URL = 'http://auth:8000/.well-known/jwks.json'


class TokenVerifier:
    """Checks the signature, issuer, audience and expiry of an access token against the issuer's JWKS"""

    def __init__(
        self,
        jwks_url: str,
        issuer: str = DEFAULT_ISSUER,
        audience: str = DEFAULT_AUDIENCE,
        leeway_seconds: int = 10,
        key_client: Any = None,
    ) -> None:
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.audience = audience
        self.leeway_seconds = leeway_seconds
        # PyJWKClient caches the keys it has fetched and refetches when it meets an unknown key id
        self._key_client = key_client or jwt.PyJWKClient(jwks_url, cache_keys=True, timeout=5)

    @classmethod
    def from_environment(cls) -> 'TokenVerifier':
        return cls(
            jwks_url=environ.get('AUTH_JWKS_URL', DEFAULT_JWKS_URL),
            issuer=environ.get('AUTH_ISSUER', DEFAULT_ISSUER),
            audience=environ.get('AUTH_AUDIENCE', DEFAULT_AUDIENCE),
        )

    async def verify(self, token: str) -> TokenClaims:
        # The key lookup may fetch the JWKS over the network, so keep it off the event loop
        return await asyncio.to_thread(self.verify_sync, token)

    def verify_sync(self, token: str) -> TokenClaims:
        try:
            key = self._key_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(
                token,
                key.key,
                algorithms=[ALGORITHM],
                issuer=self.issuer,
                audience=self.audience,
                leeway=self.leeway_seconds,
                options={'require': ['exp', 'iat', 'sub', 'iss', 'aud']},
            )
        except jwt.ExpiredSignatureError as error:
            raise TokenError('token expired') from error
        except jwt.PyJWKClientError as error:
            raise TokenError('signing key not available') from error
        except jwt.InvalidTokenError as error:
            raise TokenError('invalid token') from error

        # ADR-010: the claim is `tenant_id`, with `organization_id` as its deprecated alias; they are one value
        tenant = payload.get('tenant_id', payload.get('organization_id'))

        if 'tenant_id' in payload and 'organization_id' in payload and payload['tenant_id'] != payload['organization_id']:
            raise TokenError('token names two different tenants')

        try:
            return TokenClaims(
                subject=payload['sub'],
                organization_id=tenant if tenant is not None else payload['organization_id'],
                workspace_id=payload['workspace_id'],
                token_id=payload.get('jti'),
                roles=payload.get('roles', []),
                permissions=payload.get('permissions', []),
                issued_at=payload['iat'],
                expires_at=payload['exp'],
            )
        except (KeyError, ValidationError) as error:
            raise TokenError('token is missing required claims') from error
