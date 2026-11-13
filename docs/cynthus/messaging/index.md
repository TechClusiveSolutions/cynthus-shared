# cynthus-messaging-core

The `cynthus-messaging-core` package is the shared Python wheel that defines the complete messaging contract for the Cynthus platform. It is installed by every service that participates in the choreography bus and provides:

- **Signal naming classes** - typed, composable, read-only class-level names for every signal on the bus.
- **Payload classes** - Pydantic models that define and validate the inner data of each signal.
- **Message classes** - Pydantic models that bind a payload to the full envelope (envelope headers + payload), ready to publish or deserialise.
- **Subscription classes** - FastStream `AzureServiceBusSubscription` subclasses, one per consuming service, pre-configured with the correct queue name and topic.
- **Topic classes** - Typed wrappers around Azure Service Bus topic names.

---

## Architecture overview

All signals travel on the **Azure Service Bus** (AMQP). The bus is partitioned into three topics aligned to visibility and compliance boundaries:

- `cynthus-events-topic`: Open-source Core signals. Consumed by any authorized service.
- `cynthus-topic-internal`: Closed-source Intelligence and Health signals. Payload is opaque to open-source consumers.
- `cynthus-topic-audit`: Append-only compliance events. Separate retention and integrity policies.

This package covers **`cynthus-events-topic`** signals only. Internal and audit signals are defined in the private `cynthus-messaging-internal` wheel.

---

## Signal naming convention

Every signal name is a four-part dot-notated string:

```text
{visibility}.{domain}.{aggregate}.{action}
```

- `visibility`
  - Type: `str`
  - Example values: `public`
- `domain`
  - Type: `SignalDomainType`
  - Example values: `meal`
- `aggregate`
  - Type: `str`
  - Example values: `suggestion`, `plan`, `vote`
- `action`
  - Type: `SignalActionType`
  - Example values: `created`, `accepted`, `rejected`

Signal names are derived automatically from the signal class - they are never hardcoded strings. See [common/primitives.md](common/primitives.md) for the `SignalBase` metaclass pattern.

---

## Wire format

Every message published to the bus is a JSON object with a flat envelope wrapping a typed payload:

```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "public.meal.suggestion.requested",
  "lifecycle_action": "created",
  "correlation_id": "f0e1d2c3-b4a5-6789-cdef-012345678901",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T14:32:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T14:32:00.000000+00:00",
    "metadata": {},
    "...domain fields...": "..."
  }
}
```

All `datetime` fields are serialised as ISO 8601 UTC strings with microsecond precision and a `+00:00` suffix.

---

## Document map

Paths are relative to `docs/cynthus/messaging/`. Each line is a path, then what the page covers.

- `index.md`: you are here
- `common/`
  - `primitives.md`: SignalBase, SignalMessage, SignalPayload, all enums
- `component/`
  - `identity/`
    - `index.md`: identity domain overview
    - `user.md`: identity.user.* signals
    - `token.md`: identity.token.* signals
    - `access.md`: identity.access.* signals
  - `inventory/`
    - `index.md`: inventory domain overview
    - `request.md`: inventory request and response signals
    - `location.md`: inventory.location.* signals
    - `shelf.md`: inventory.shelf.* signals
    - `item.md`: inventory.item.* signals
  - `meal/`
    - `index.md`: meal domain overview and signal flow
    - `plan.md`: meal.plan.* signals
    - `rating.md`: meal.rating.* signals
    - `recipes.md`: meal.recipes.* signals
    - `suggestion.md`: meal.suggestion.* signals
    - `tag.md`: meal.tag.* signals
    - `vote.md`: meal.vote.* signals
- `broker.md`: choosing the broker: Service Bus or RabbitMQ
- `subscription.md`: all per-service subscription classes
- `topic.md`: topic classes

---

## Adding a new signal

1. Add any new `SignalActionType` or `SignalDomainType` values to the enums in `common/signal/`.
2. Create an aggregate base class (`public_{domain}_{aggregate}_base.py`) passing `abstract=True`.
3. Create one concrete signal class per action (`public_{domain}_{aggregate}_{action}.py`).
4. Create the payload class in `component/{domain}/payload/`.
5. Create the message class in `component/{domain}/message/`.
6. Export all new classes from the relevant `__init__.py` files.
7. Add a documentation entry to the appropriate file under `docs/cynthus/messaging/component/`.

The `__init_subclass__` guard in `SignalBase` will raise a `TypeError` at import time if any of `domain`, `aggregate`, or `action` is missing from a concrete signal class.

---

## Tenant id (ADR-010)

Every signal carries `tenant_id`, the tenant the signal belongs to. `organization_id` is its deprecated alias and holds the same value: you may give either when you build a message, both are written to the JSON, and two different values are refused. A signal from a publisher that knows only `organization_id` still reads. The same holds for access tokens: they carry both `tenant_id` and `organization_id` claims with one value, the verifier accepts either, and `TokenClaims.tenant_id` gives the value. `organization_id` is removed after one release.
