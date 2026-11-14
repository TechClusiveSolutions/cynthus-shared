"""Access token issuer for the Cynthus project"""

import base64
import hashlib
import time
from typing import Any, Dict, Iterable
from uuid import UUID, uuid4

import jwt
from cryptography.hazmat.primitives import serialization
from jwt.algorithms import RSAAlgorithm

from .issued_token import IssuedToken

ALGORITHM = 'RS256'


class TokenIssuer:
    """Signs access tokens with an RSA private key and publishes the matching public key as a JWKS"""

    def __init__(self, private_key_pem: str | bytes, issuer: str, audience: str, ttl_seconds: int = 900) -> None:
        if isinstance(private_key_pem, str):
            private_key_pem = private_key_pem.encode('utf-8')

        self._private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        self.issuer = issuer
        self.audience = audience
        self.ttl_seconds = ttl_seconds

        public_der = self._private_key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.key_id = base64.urlsafe_b64encode(hashlib.sha256(public_der).digest()).decode('ascii').rstrip('=')

    def issue(
        self,
        subject: UUID,
        organization_id: UUID,
        workspace_id: UUID,
        roles: Iterable[str] = (),
        permissions: Iterable[str] = (),
        owner: bool = False,
    ) -> str:
        return self.issue_token(subject, organization_id, workspace_id, roles, permissions, owner).token

    def issue_token(
        self,
        subject: UUID,
        organization_id: UUID,
        workspace_id: UUID,
        roles: Iterable[str] = (),
        permissions: Iterable[str] = (),
        owner: bool = False,
    ) -> IssuedToken:
        issued_at = int(time.time())
        token_id = str(uuid4())

        claims = {
            'iss': self.issuer,
            'aud': self.audience,
            'sub': str(subject),
            'jti': token_id,
            'iat': issued_at,
            'exp': issued_at + self.ttl_seconds,
            'organization_id': str(organization_id),
            'tenant_id': str(organization_id),
            'workspace_id': str(workspace_id),
            'roles': list(roles),
            'permissions': list(permissions),
            # True only when the subject owns the tenant of the token (ADR-010); never derived from roles
            'owner': owner is True,
        }

        token = jwt.encode(claims, self._private_key, algorithm=ALGORITHM, headers={'kid': self.key_id})

        return IssuedToken(token=token, token_id=token_id, key_id=self.key_id, expires_in=self.ttl_seconds)

    def jwks(self) -> Dict[str, Any]:
        key = RSAAlgorithm.to_jwk(self._private_key.public_key(), as_dict=True)
        key.update({'kid': self.key_id, 'use': 'sig', 'alg': ALGORITHM})

        return {'keys': [key]}
