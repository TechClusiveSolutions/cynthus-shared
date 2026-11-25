# EventHooks (`cynthus.core.event.EventHooks`)

A hook point for events: code that wants to know when an event happens registers a hook, and whoever has the event fires it. It works for an `Event` and for a [SignalEvent](signal_event.md).

---

## Use

- `register(event_class, hook)`: `hook` is an async function that takes the event and returns nothing.
- `await fire(event)`: awaits, in registration order, every hook registered for the class of the event or for any base class of it. A hook registered for `SignalEvent` therefore sees every signal event, and a hook for a class that is not in the event's ancestry is not called.

A hook registered while `fire` is running first runs on the next `fire`.

Each `EventHooks` object has its own list of hooks; nothing is shared between objects.

```python
hooks = EventHooks()


async def audit(event: SignalEvent) -> None:
    ...


hooks.register(SignalEvent, audit)
await hooks.fire(event)
```

---

## Failures

- A hook that raises is logged at error level with the event type, and the next hook still runs. The failure is not passed on to whoever fires the event.
- `asyncio.CancelledError` is never swallowed.
- Firing an event with no hooks returns at once.
- A hook receives the event only and cannot change it: a `SignalEvent` is frozen.
