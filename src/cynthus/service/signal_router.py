"""Signal Router class for the Cynthus project"""

import inspect
import re

from cynthus.core.event import Event, SignalEvent
from cynthus.messaging.common.signal.message_base import SignalMessageBase
from cynthus.messaging.publisher import EventMessagePublisher, SignalPublisher
from cynthus.messaging.registry import SignalGeneratorRegistry
from cynthus.messaging.subscriber import ReceivedSignal

from .unknown_signal_error import UnknownSignalError

SIGNAL_NAME = re.compile(r'^[a-z]+(\.[a-z_]+){3}$')


class SignalRouter:
    """
        Runs the function registered for a received signal and publishes what it returns

        Functions are registered by signal name with ``subscriber`` and run by ``ServiceModule(handler=router.dispatch)``
        through the platform path (``SignalBroker``), so the router never names a broker. A function is
        ``async def f(signal, publisher)`` and returns ``None``, a ready message, an ``Event`` or a ``SignalEvent``.
        An ``exception_handler`` turns an exception into the result to publish. A function or handler that raises
        propagates, so the signal is dead-lettered. Published answers carry no access token.
    """

    def __init__(self, registry: SignalGeneratorRegistry | None = None) -> None:
        self._registry = SignalGeneratorRegistry.default() if registry is None else registry
        self._functions: dict = {}
        self._exception_handlers: dict = {}

    def subscriber(self, signal_name: str):
        """Decorator: register an ``async def (signal, publisher)`` function for ``signal_name`` and return it unchanged"""

        if not isinstance(signal_name, str) or not SIGNAL_NAME.fullmatch(signal_name):
            raise ValueError(f'{signal_name!r} is not a signal name')

        if signal_name in self._functions:
            raise ValueError(f'A function is already registered for the signal {signal_name!r}')

        def register(function):
            if not inspect.iscoroutinefunction(function):
                raise TypeError(f'The function for {signal_name!r} must be a coroutine function (async def)')

            # Checked again: two decorators made for one name must not replace each other
            if signal_name in self._functions:
                raise ValueError(f'A function is already registered for the signal {signal_name!r}')

            self._functions[signal_name] = function

            return function

        return register

    def exception_handler(self, exception_type: type[Exception]):
        """Decorator: register an ``async def (error, signal)`` function that returns the result to publish for an error"""

        if not (isinstance(exception_type, type) and issubclass(exception_type, Exception)):
            raise TypeError(f'{exception_type!r} is not an Exception subclass')

        if exception_type in self._exception_handlers:
            raise ValueError(f'A handler is already registered for {exception_type.__name__}')

        def register(function):
            if not inspect.iscoroutinefunction(function):
                raise TypeError(f'The handler for {exception_type.__name__} must be a coroutine function (async def)')

            if exception_type in self._exception_handlers:
                raise ValueError(f'A handler is already registered for {exception_type.__name__}')

            self._exception_handlers[exception_type] = function

            return function

        return register

    async def dispatch(self, signal: ReceivedSignal, publisher: SignalPublisher) -> None:
        """Run the function of ``signal`` and publish its result; an unknown signal raises ``UnknownSignalError``"""

        function = self._functions.get(signal.event_type)

        if function is None:
            raise UnknownSignalError(signal.event_type)

        try:
            result = await function(signal, publisher)
        except Exception as error:
            handler = next(
                (self._exception_handlers[klass] for klass in type(error).__mro__ if klass in self._exception_handlers),
                None,
            )

            if handler is None:
                raise

            result = await handler(error, signal)

        await self._publish(result, publisher)

    async def _publish(self, result, publisher: SignalPublisher) -> None:
        if result is None:
            return

        if isinstance(result, SignalMessageBase):
            await publisher.publish(result)
        elif isinstance(result, (Event, SignalEvent)):
            await EventMessagePublisher(publisher, self._registry).publish(result)
        else:
            raise TypeError(f'A function cannot return {type(result).__name__}; return None, a message or an event')
