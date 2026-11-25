# SignalEvent (`cynthus.core.event.SignalEvent`)

An event that a received signal can become. The `Event` class needs whole `Tenant`, `Workspace` and `Resource` objects, and a request signal with its token carries only ids (`TokenClaims`). A segment may not read another segment's database (ADR-014), so it cannot build those objects. `SignalEvent` is built from ids alone. `Event` and the existing event classes are unchanged.

---

## Fields

- `id_`: a UUID, new for each event.
- `correlation_id`: a UUID, new unless given, so the events of one request can share it.
- `occurred_on`: a timezone-aware UTC time, now unless given.
- `tenant_id`, `workspace_id`, `actor_id`: UUIDs, required. The actor is who asked.
- `service_id`: the service that recorded the event, or `None`.
- `action`: an `EventAction`. A read request is `EventAction.RETRIEVED`.
- `data`: a dictionary, required.

The event is frozen: assigning a field raises an error. To answer an event, build a new one. The `data` field is a copy of the dictionary that was given. Its content can still be changed in place; do not do that, because the parsed data would be stale.

`model_copy(update=...)` validates the copy again (the action and `data_model` checks run and the parsed data is rebuilt). The copy keeps `id_` unless `update` changes it. An `update` key that is not a field raises `ValueError`. Without `deep=True` the copy shares nested values, such as a list inside `data`, with the original.

The event can be hashed: the hash is the hash of `id_`, which is consistent with equality, because equal events have equal ids.

---

## Typed data and allowed actions

A subclass can set two class variables.

- `data_model`: a pydantic model. `data` is validated when the event is created, and `parsed_data(model)` returns the model parsed then (the same object each time), so the data is parsed once. A data model should use `extra='forbid'`, so an unknown key fails with a `ValidationError`. A missing required field fails the same way.
- `actions`: a `frozenset` of `EventAction`. An event created with any other action raises a `ValidationError`.

`event_type` is the snake_case class name without a trailing `Event`: `ThingHappenedEvent` is `thing_happened` and `SignalEvent` is `signal`.

```python
class ThingHappenedEvent(SignalEvent):
    data_model = ThingHappenedData
    actions = frozenset({EventAction.RETRIEVED})


event = ThingHappenedEvent(tenant_id=claims.tenant_id, workspace_id=claims.workspace_id,
                           actor_id=claims.actor_id, action=EventAction.RETRIEVED, data={'name': 'x'})
data = event.parsed_data(ThingHappenedData)
```

Hooks for events are described in [EventHooks](event_hooks.md).
