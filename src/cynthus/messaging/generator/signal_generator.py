"""Signal Generator class for the Cynthus project"""

from __future__ import annotations

import re
from abc import ABC
from typing import Any, ClassVar

from ...core.event import Event, SignalEvent, SystemEvent, UserEvent
from ..common.signal.lifecycle_action import LifecycleAction
from ..common.signal.message_base import SignalMessageBase
from ..common.signal.payload import SignalPayload
from ..registry.unknown_event_error import UnknownEventError
from .signal_contract import SignalContract

SOURCE = re.compile(r'^((data|resource|user|tenant|workspace)\.[a-z_][a-z0-9_]*|env\.[A-Za-z_][A-Za-z0-9_]*)$')
LIFECYCLE_VALUES = {a.value for a in LifecycleAction}


class SignalGenerator(ABC):
    """
        Turns one event into one signal message; a pure function of the event

        A subclass sets ``contracts`` and adds one method per contract, ``created(self, event)`` for example, which
        builds the payload and returns ``contract.message(**self.envelope(event, contract), payload=payload)``.
        No I/O, no lookups, no clock, no change to the event. See ``docs/signal-generators.md``.
    """

    contracts: ClassVar[tuple[SignalContract, ...]] = ()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        events: set[str] = set()
        signals: set[str] = set()
        base_fields = set(SignalPayload.model_fields)

        for contract in cls.contracts:
            name = f'{cls.__name__}.{contract.method}'

            if not callable(getattr(cls, contract.method, None)):
                raise TypeError(f'{cls.__name__} has no method {contract.method}')

            if contract.message.model_fields['event_type'].default != contract.signal.name:
                raise TypeError(f'{name}: the event_type of {contract.message.__name__} is not {contract.signal.name}')

            missing = sorted(set(contract.payload.model_fields) - base_fields - set(contract.sources))

            if missing:
                raise TypeError(f'{name}: no source for the payload fields {", ".join(missing)}')

            extra = sorted(set(contract.sources) - set(contract.payload.model_fields))

            if extra:
                raise TypeError(f'{name}: sources for fields the payload does not have: {", ".join(extra)}')

            bad = sorted(f for f, source in contract.sources.items() if not SOURCE.match(source))

            if bad:
                raise TypeError(f'{name}: malformed source for {", ".join(bad)}; see docs/signal-generators.md')

            if contract.signal.action.value in LIFECYCLE_VALUES and contract.lifecycle_action.value != contract.signal.action.value:
                raise TypeError(
                    f'{name}: the lifecycle action {contract.lifecycle_action.value} does not match the signal '
                    f'action {contract.signal.action.value}'
                )

            if contract.event in events:
                raise TypeError(f'{cls.__name__}: two contracts for the event {contract.event}')

            if contract.signal.name in signals:
                raise TypeError(f'{cls.__name__}: two contracts for the signal {contract.signal.name}')

            events.add(contract.event)
            signals.add(contract.signal.name)

    def generate(self, event: Event | SignalEvent) -> SignalMessageBase:
        """The signal message for ``event``; ``UnknownEventError`` when no contract matches its class name"""

        name = type(event).__name__

        for contract in self.contracts:
            if contract.event == name:
                return getattr(self, contract.method)(event)

        raise UnknownEventError(f'{type(self).__name__} has no contract for the event {name}')

    def contract(self, method: str) -> SignalContract:
        """The contract of the generator method named ``method``"""

        for contract in self.contracts:
            if contract.method == method:
                return contract

        raise LookupError(f'{type(self).__name__} has no contract for the method {method}')

    def envelope(self, event: Event | SignalEvent, contract: SignalContract) -> dict[str, Any]:
        """
            The envelope fields of the message: who, what, when and where

            A ``SignalEvent`` carries the ids itself. For an ``Event`` the ids come from its tenant, workspace and
            user or system; ``ValueError`` when it has neither a user nor a system.
        """

        if isinstance(event, SignalEvent):
            tenant_id = event.tenant_id
            workspace_id = event.workspace_id
            actor_id = event.actor_id
        elif isinstance(event, UserEvent):
            tenant_id = event.tenant.id_
            workspace_id = event.workspace.id_
            actor_id = event.user.id_
        elif isinstance(event, SystemEvent):
            tenant_id = event.tenant.id_
            workspace_id = event.workspace.id_
            actor_id = event.system.id_
        else:
            raise ValueError(f'The event {type(event).__name__} has neither a user nor a system as actor')

        return {
            'event_id': event.id_,
            'timestamp': event.occurred_on,
            'tenant_id': tenant_id,
            'workspace_id': workspace_id,
            'correlation_id': event.correlation_id,
            'actor_id': actor_id,
            'event_type': contract.signal.name,
            'lifecycle_action': contract.lifecycle_action,
        }
