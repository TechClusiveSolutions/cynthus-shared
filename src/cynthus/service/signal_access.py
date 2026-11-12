"""Checks that a signal was sent on behalf of a caller who may ask for it."""

from cynthus.core import logging
from cynthus.security import AccessRecorder, BearerToken, TokenClaims, TokenError, TokenVerifier

from .forbidden import Forbidden

LOGGER = logging.getLogger(__name__)

AUTHORIZATION = 'authorization'


class SignalAccess:
    """The API forwards the caller's access token as the `authorization` message property (read from a Service Bus
    message or from a `ReceivedSignal`).

    A signal is answered only when that token is genuine, grants the permission, and names the same organization,
    workspace and actor as the signal itself, so a signal cannot be forged or replayed for another tenant.
    """

    def __init__(self, verifier: TokenVerifier | None = None, recorder: AccessRecorder | None = None) -> None:
        self._verifier = verifier
        # Told about every decision; set when the application starts so refusals become audit signals
        self.recorder = recorder

    @property
    def verifier(self) -> TokenVerifier:
        if self._verifier is None:
            self._verifier = TokenVerifier.from_environment()

        return self._verifier

    async def authorize(self, message, signal_message, permission: str) -> TokenClaims:
        logger = LOGGER.getChild('authorize')

        resource, method = signal_message.event_type, 'SIGNAL'

        try:
            claims = await self.verifier.verify(BearerToken.extract(self._header(message)))
        except TokenError as error:
            logger.warning('Refused signal %s: %s', signal_message.event_id, error.reason)

            await self._record('rejected', error.reason, resource, method)

            raise

        if not claims.has_permission(permission):
            logger.warning('Refused signal %s: the token lacks %s', signal_message.event_id, permission)

            await self._record('denied', claims, permission, resource, method)

            raise Forbidden(f'the token does not grant {permission}')

        if not claims.has_workspace:
            logger.warning('Refused signal %s: the token has no workspace', signal_message.event_id)

            await self._record('rejected', 'workspace_required', resource, method)

            raise Forbidden('workspace_required')

        if (claims.organization_id, claims.workspace_id, claims.subject) != (
            signal_message.organization_id, signal_message.workspace_id, signal_message.actor_id,
        ):
            logger.warning('Refused signal %s: the token belongs to another caller', signal_message.event_id)

            await self._record('rejected', 'the token does not match the signal', resource, method)

            raise TokenError('the token does not match the signal')

        await self._record('granted', claims, permission, resource, method)

        return claims

    async def _record(self, decision: str, *arguments) -> None:
        if self.recorder is None:
            return

        try:
            await getattr(self.recorder, decision)(*arguments)
        except Exception:
            LOGGER.getChild('_record').exception('Could not record the %s access decision', decision)

    @staticmethod
    def _header(message) -> str | bytes | None:
        # A raw Service Bus message keeps its properties in `application_properties`, with bytes keys; a
        # `ReceivedSignal` keeps them in `properties`, as text. Accept either.
        properties = getattr(message, 'application_properties', None) or getattr(message, 'properties', None) or {}

        for key, value in properties.items():
            name = key.decode('utf-8', errors='replace') if isinstance(key, bytes) else key

            if name.lower() == AUTHORIZATION:
                return value

        return None
