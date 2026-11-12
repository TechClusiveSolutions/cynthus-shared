"""Route dependency that lets a request through only when its access token grants a permission."""

from fastapi import FastAPI, Request

from cynthus.core import logging

from .access_denied import AccessDenied
from .access_recorder import AccessRecorder
from .bearer_token import BearerToken
from .token_claims import TokenClaims
from .token_error import TokenError

LOGGER = logging.getLogger(__name__)

WORKSPACE_REQUIRED = 'workspace_required'


class RequirePermission:
    """Use as `Depends(RequirePermission('inventory:read'))`; the route receives the verified `TokenClaims`.

    Needs `app.state.token_verifier`. When `app.state.access_recorder` is set it is told about every decision.
    """

    def __init__(self, permission: str) -> None:
        self.permission = permission

    async def __call__(self, request: Request) -> TokenClaims:
        resource, method = request.url.path, request.method

        try:
            token = BearerToken.extract(request.headers.get('authorization'))
        except TokenError as error:
            await self._record(request.app, 'rejected', error.reason, resource, method)

            raise AccessDenied(401, error.reason) from error

        claims = await self.authorize(request.app, token, resource, method)

        # Kept so the route can forward the caller's token on the signals it publishes
        request.state.access_token = token

        return claims

    async def authorize(self, application: FastAPI, token: str, resource: str = '', method: str = '') -> TokenClaims:
        logger = LOGGER.getChild('authorize')

        try:
            claims = await application.state.token_verifier.verify(token)
        except TokenError as error:
            logger.info('Refused a request: %s', error.reason)

            await self._record(application, 'rejected', error.reason, resource, method)

            raise AccessDenied(401, error.reason) from error

        if not claims.has_permission(self.permission):
            logger.info('Refused %s: the token lacks %s', claims.subject, self.permission)

            await self._record(application, 'denied', claims, self.permission, resource, method)

            raise AccessDenied(403, f'the token does not grant {self.permission}')

        if not claims.has_workspace:
            logger.info('Refused %s: the token has no workspace', claims.subject)

            await self._record(application, 'rejected', WORKSPACE_REQUIRED, resource, method)

            raise AccessDenied(409, 'make or choose a workspace first', WORKSPACE_REQUIRED)

        await self._record(application, 'granted', claims, self.permission, resource, method)

        return claims

    @staticmethod
    async def _record(application: FastAPI, decision: str, *arguments) -> None:
        recorder: AccessRecorder | None = getattr(application.state, 'access_recorder', None)

        if recorder is None:
            return

        try:
            await getattr(recorder, decision)(*arguments)
        except Exception:
            LOGGER.getChild('_record').exception('Could not record the %s access decision', decision)
