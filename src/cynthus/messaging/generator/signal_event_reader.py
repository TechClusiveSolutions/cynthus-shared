"""Signal Event Reader class for the Cynthus project"""

from __future__ import annotations

from ...core.event import EventAction, SignalEvent
from ...security.token_claims import TokenClaims
from ..common.signal.message_base import SignalMessageBase
from ..registry.signal_generator_registry import SignalGeneratorRegistry
from .signal_event_mismatch import SignalEventMismatch


class SignalEventReader:
    """
        Builds a ``SignalEvent`` from a received signal message and the verified token claims

        The contract of the event class is read in reverse: the payload fields that the contract maps to ``data.*``
        become the data of the event. The ids come from the claims, after they are checked against the message.
        See ``docs/signal-generators.md``.
    """

    def __init__(self, registry: SignalGeneratorRegistry | None = None) -> None:
        self._registry = registry if registry is not None else SignalGeneratorRegistry.default()

    def read(
        self,
        message: SignalMessageBase,
        claims: TokenClaims,
        event_class: type[SignalEvent],
        action: EventAction | None = None,
    ) -> SignalEvent:
        """
            The event of ``event_class`` that ``message`` asks for

            ``UnknownEventError`` when no contract is registered for the class; ``SignalEventMismatch`` when the signal
            or an id differs from the claims; ``ValueError`` when a source cannot be read back or no action is known;
            the event's own ``ValidationError`` when the data or the action is refused.
        """

        contract = self._registry.contract_for(event_class.__name__)

        if message.event_type != contract.signal.name:
            raise SignalEventMismatch('The signal does not match the event class (event_type)')

        for name, expected in (
            ('tenant_id', claims.tenant_id),
            ('workspace_id', claims.workspace_id),
            ('actor_id', claims.subject),
        ):
            if getattr(message, name) != expected:
                raise SignalEventMismatch(f'The signal does not match the token claims ({name})')

        if not isinstance(message.payload, contract.payload):
            raise SignalEventMismatch('The signal does not match the event class (payload)')

        # JSON mode: ids, times and enums as text, like the data of an event built from a request; the data model of
        # the event parses them back
        dumped = message.payload.model_dump(mode='json')
        data = {}

        for field, source in contract.sources.items():
            if source.startswith('data.'):
                data[source[5:]] = dumped[field]
            elif source.startswith(('resource.', 'user.')):
                raise ValueError(f'The payload field {field} comes from {source}, which a signal event cannot read back')

        if action is None:
            if event_class.actions is None or len(event_class.actions) != 1:
                raise ValueError('action is required')

            (action,) = event_class.actions

        return event_class(
            id_=message.event_id,
            correlation_id=message.correlation_id,
            occurred_on=message.timestamp,
            tenant_id=claims.tenant_id,
            workspace_id=claims.workspace_id,
            actor_id=claims.subject,
            action=action,
            data=data,
        )
