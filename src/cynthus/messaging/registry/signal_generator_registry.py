"""Signal Generator Registry class for the Cynthus project"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import TYPE_CHECKING

from ...core.event import Event, SignalEvent
from ..common.signal.base import SignalBase
from .unknown_event_error import UnknownEventError

if TYPE_CHECKING:
    from ..generator.signal_contract import SignalContract
    from ..generator.signal_generator import SignalGenerator

SIGNAL_NAME = re.compile(r'^[a-z]+(\.[a-z_]+){3}$')


class SignalGeneratorRegistry:
    """
        Maps the class name of an event to the generator that turns it into a signal message

        Built from the contracts of the generator classes. The registry holds event names, not event classes, so it
        imports no event module. Each generator is created once, without arguments. See ``docs/signal-generators.md``.
    """

    def __init__(self, generators: Iterable[type[SignalGenerator]] | None = None) -> None:
        self._generators: dict[str, SignalGenerator] = {}
        self._contracts: dict[str, SignalContract] = {}
        self._events: dict[str, str] = {}

        for generator in generators or ():
            self.register(generator)

    def register(self, generator: type[SignalGenerator]) -> None:
        """Register every contract of ``generator``; ``ValueError`` when one is invalid or already registered"""

        from ..generator.signal_generator import SignalGenerator

        if not isinstance(generator, type) or not issubclass(generator, SignalGenerator):
            raise ValueError(f'{generator!r} is not a signal generator class')

        instance = generator()

        # Check every contract first so a failure leaves the registry unchanged
        for contract in generator.contracts:
            signal = contract.signal

            if not isinstance(contract.event, str) or not contract.event:
                raise ValueError('event_name must be a non-empty string')

            if not isinstance(signal, type) or not issubclass(signal, SignalBase):
                raise ValueError(f'{signal!r} is not a signal class')

            if any(not hasattr(signal, f) for f in ('domain', 'aggregate', 'action')):
                raise ValueError(f'{signal.__name__} is abstract; register a concrete signal')

            if not SIGNAL_NAME.match(signal.name):
                raise ValueError(f'{signal.name!r} is not a valid signal name')

            if contract.event in self._generators:
                raise ValueError(f'{contract.event} is already registered')

            if signal.name in self._events:
                raise ValueError(f'{signal.name} is already registered (for {self._events[signal.name]})')

        for contract in generator.contracts:
            signal = contract.signal
            self._generators[contract.event] = instance
            self._contracts[contract.event] = contract
            self._events[signal.name] = contract.event

    def generator_for(self, event: Event | SignalEvent | str) -> SignalGenerator:
        """The generator for an event instance or an event class name; ``UnknownEventError`` when absent"""

        name = event if isinstance(event, str) else type(event).__name__

        try:
            return self._generators[name]
        except KeyError:
            raise UnknownEventError(f'No signal generator is registered for the event {name}') from None

    def signal_for(self, event: Event | SignalEvent | str) -> type[SignalBase]:
        """The signal class for an event instance or an event class name; ``UnknownEventError`` when absent"""

        name = event if isinstance(event, str) else type(event).__name__

        try:
            return self._contracts[name].signal
        except KeyError:
            raise UnknownEventError(f'No signal generator is registered for the event {name}') from None

    def contract_for(self, event: Event | SignalEvent | str) -> SignalContract:
        """The contract for an event instance or an event class name; ``UnknownEventError`` when absent"""

        name = event if isinstance(event, str) else type(event).__name__

        try:
            return self._contracts[name]
        except KeyError:
            raise UnknownEventError(f'No signal generator is registered for the event {name}') from None

    def event_name_for(self, signal: type[SignalBase]) -> str:
        """The event class name registered for ``signal``; ``UnknownEventError`` when absent"""

        name = getattr(signal, 'name', None)

        try:
            return self._events[name]
        except (KeyError, TypeError):
            raise UnknownEventError(
                f'No event is registered for the signal {getattr(signal, "__name__", repr(signal))}'
            ) from None

    def contracts(self) -> tuple[SignalContract, ...]:
        """The registered contracts, sorted by event class name"""

        return tuple(self._contracts[name] for name in sorted(self._contracts))

    def __contains__(self, event_name: object) -> bool:
        return event_name in self._generators

    def __len__(self) -> int:
        return len(self._generators)

    def event_names(self) -> tuple[str, ...]:
        """The registered event class names, sorted"""

        return tuple(sorted(self._generators))

    @classmethod
    def default(cls) -> SignalGeneratorRegistry:
        """A new registry holding the built-in generators"""

        from ..component.inventory.generator import InventoryLocationSignalGenerator, InventoryShelfSignalGenerator
        from ..component.partner.generator import PartnerSignalGenerator

        return cls([InventoryLocationSignalGenerator, InventoryShelfSignalGenerator, PartnerSignalGenerator])
