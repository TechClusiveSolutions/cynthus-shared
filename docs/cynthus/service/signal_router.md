# SignalRouter (`cynthus.service.SignalRouter`)

A decorator style subscriber: functions are registered by signal name, `ServiceModule` runs them through the platform path (`SignalBroker`, ADR-007), and what a function returns is published. It is not a FastStream broker; it never names a broker.

---

## Use

```python
from cynthus.messaging.component.partner import PartnerServiceListRespondedMessage
from cynthus.messaging.publisher import SignalPublisher
from cynthus.messaging.subscriber import ReceivedSignal
from cynthus.service import ApiError, ServiceModule, SignalRouter

router = SignalRouter()


@router.subscriber('public.partner.service_list.requested')
async def list_services(signal: ReceivedSignal, publisher: SignalPublisher):
    return PartnerServiceListRespondedMessage(...)


@router.exception_handler(ApiError)
async def api_error(error: ApiError, signal: ReceivedSignal):
    return PartnerServiceListRespondedMessage(...)


ServiceModule(service=service, subscription=subscription, handler=router.dispatch)
```

- `SignalRouter(registry=None)`: the registry finds the generator of an `Event` or `SignalEvent` result (`SignalGeneratorRegistry.default()` when omitted).
- `subscriber(signal_name)`: registers an `async def (signal, publisher)` function and returns it unchanged. `ValueError` for a name that is not a signal name (`^[a-z]+(\.[a-z_]+){3}$`) or that is already registered; `TypeError` for a function that is not `async def`.
- `exception_handler(exception_type)`: registers an `async def (error, signal)` function that returns what to publish for that exception. `TypeError` for a function that is not `async def` or a type that is not an `Exception` subclass; `ValueError` for a type registered twice.
- `await dispatch(signal, publisher)`: what `ServiceModule` is given as `handler`.

---

## What `dispatch` does

1. Finds the function for `signal.event_type`. With none it raises `UnknownSignalError` before anything runs, so a misrouted signal is dead-lettered and visible.
2. Awaits `function(signal, publisher)`.
3. If the function raises an `Exception`, the handler of the nearest class in the exception's MRO answers instead (a handler for a subclass beats one for its base). With no handler, the original exception propagates. An exception raised by a handler propagates. `asyncio.CancelledError` and other `BaseException`s are never handled.
4. Publishes the result: `None` publishes nothing; a `SignalMessageBase` is published as is; an `Event` or `SignalEvent` is published through `EventMessagePublisher` and the registry; anything else raises `TypeError` and publishes nothing. No access token is attached.
5. An error from publishing propagates.

Whatever propagates reaches `SignalConsumer`, which dead-letters the signal with the reason `processing_failed`; a signal that returns normally is completed.

Dependency injection is not part of the router yet: a function takes `(signal, publisher)` only.
