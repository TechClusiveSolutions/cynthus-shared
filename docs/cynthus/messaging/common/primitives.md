# Common Primitives

These classes form the structural foundation that every signal, payload, and message in the package inherits from. They are defined in `src/cynthus/messaging/common/signal/` and re-exported from `cynthus.messaging.common`.

---

## Enumerations

### `LifecycleAction`

**Module:** `cynthus.messaging.common.signal.lifecycle_action`

The four canonical state-mutation verbs used on all Pydantic entity models. Constraining mutations to these four values prevents event-type explosion on the bus.

- `CREATED`
  - String: `"created"`
  - Usage: A new entity was persisted for the first time.
- `UPDATED`
  - String: `"updated"`
  - Usage: One or more fields on an existing entity changed.
- `DELETED`
  - String: `"deleted"`
  - Usage: An entity was removed or soft-deleted.
- `SNAPSHOT`
  - String: `"snapshot"`
  - Usage: A full point-in-time state capture, typically from a scheduled job or reconciliation pass.

Every `SignalMessage` carries a `lifecycle_action` field typed to this enum. Downstream consumers use it to decide how to apply the incoming payload to their local state - they do not need to parse `event_type` to determine mutation semantics.

---

### `SignalActionType`

**Module:** `cynthus.messaging.common.signal.action_type`

Extended action vocabulary for the `action` component of a signal name. The four `LifecycleAction` values cover entity mutations; `SignalActionType` adds domain-event verbs for aggregates that have richer lifecycle semantics.

- `ACCEPTED`
  - String: `"accepted"`
  - Used by: `meal.suggestion.accepted`
- `ASSOCIATED`
  - String: `"associated"`
  - Used by: `meal.recipes.associated`
- `AUTO_RESOLVED`
  - String: `"auto_resolved"`
  - Used by: `meal.vote.auto_resolved`
- `CAST`
  - String: `"cast"`
  - Used by: `meal.vote.cast`
- `CREATED`
  - String: `"created"`
  - Used by: `meal.plan.created`, `meal.tag.created`, `meal.rating.created`
- `DELETED`
  - String: `"deleted"`
  - Used by: `meal.plan.deleted`, `meal.tag.deleted`, `meal.rating.deleted`
- `GENERATED`
  - String: `"generated"`
  - Used by: `meal.suggestion.generated`
- `INITIATED`
  - String: `"initiated"`
  - Used by: `meal.vote.initiated`
- `REJECTED`
  - String: `"rejected"`
  - Used by: `meal.suggestion.rejected`
- `REQUESTED`
  - String: `"requested"`
  - Used by: `meal.suggestion.requested`
- `RESOLVED`
  - String: `"resolved"`
  - Used by: `meal.vote.resolved`
- `UPDATED`
  - String: `"updated"`
  - Used by: `meal.plan.updated`, `meal.rating.updated`

---

### `SignalDomainType`

**Module:** `cynthus.messaging.common.signal.domain_type`

The `domain` component of a signal name, typed as a `str` enum.

- `MEAL`
  - String: `"meal"`
  - Description: All meal planning, suggestion, voting, and rating signals.

Additional domains (`device`, `inventory`, `auth`, `clinical`) are not yet registered in this enum - their signals currently use hardcoded `event_type` strings and have not been migrated to the `SignalBase` metaclass pattern.

---

## Base Classes

### `SignalBase`

**Module:** `cynthus.messaging.common.signal.base`

A plain Python class (not a Pydantic model) that establishes the typed naming contract for every signal. Uses a custom metaclass (`_SignalMeta`) to expose a read-only, composable `name` property at the class level.

**Class variables** (typed as `ClassVar` for IDE support):

- `visibility`
  - Type: `str`
  - Description: Always `'public'` for open-source signals.
- `domain`
  - Type: `SignalDomainType`
  - Description: The functional area of the signal.
- `aggregate`
  - Type: `str`
  - Description: The entity or lifecycle concept being described.
- `action`
  - Type: `SignalActionType`
  - Description: The specific event within the aggregate's lifecycle.

**`name` property (read-only, class-level):**

```python
PublicMealSuggestionRejectedSignal.name
# -> "public.meal.suggestion.rejected"

PublicMealSuggestionRejectedSignal.name = "Bob"
# -> AttributeError: can't set attribute
```

`name` is implemented as a property on the metaclass. Accessing it on the class returns the composed string. It has no setter, so assignment raises `AttributeError` immediately - no guard code needed.

**`__init_subclass__` validation:**

Concrete subclasses that do not pass `abstract=True` are validated at import time. If `domain`, `aggregate`, or `action` is missing, a `TypeError` is raised before the class is usable:

```python
class BrokenSignal(SignalBase):
    domain = SignalDomainType.MEAL
    # forgot aggregate and action

# ImportError -> TypeError: BrokenSignal must define the following signal component(s): aggregate, action
```

Intermediate abstract bases opt out by passing `abstract=True`:

```python
class PublicMealSignalBase(SignalBase, abstract=True):
    domain = SignalDomainType.MEAL
```

---

### `SignalPart`

**Module:** `cynthus.messaging.common.signal.part`

The root Pydantic `BaseModel` for all structural message components. Sets `frozen=True` (all instances are immutable after construction) and `populate_by_name=True`.

All payload and message classes inherit from `SignalPart` through either `SignalPayload` or `SignalMessageBase`.

---

### `SignalPayload`

**Module:** `cynthus.messaging.common.signal.payload`

The base class for all inner payload objects. Every domain payload class extends this. It provides three fields that every payload carries regardless of domain:

- `schema_version`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: Monotonically increasing version tracker. Must be `>= 1`. Increment when payload fields change in a breaking way.
- `observed_at`
  - Type: `datetime`
  - Required: No
  - Default: `utcnow()`
  - Description: The precise moment the underlying fact was observed at the edge, before any processing. Serialised as ISO 8601 UTC.
- `metadata`
  - Type: `dict[str, Any] | None`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry (e.g. `execution_ms`, `retry_count`, `source_ip`). Never use for business data.

**Serialisation note:** `observed_at` is serialised by a `@field_serializer` that enforces UTC and ISO 8601 format with microsecond precision, regardless of the input timezone.

---

### `SignalMessageBase`

**Module:** `cynthus.messaging.common.signal.message_base`

The envelope that wraps every payload published to the bus. Enforces multi-tenant isolation via `organization_id` and `workspace_id` on every message.

- `event_id`
  - Type: `UUID`
  - Required: No
  - Default: `uuid4()`
  - Description: Unique identifier for this specific message instance.
- `event_type`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: Dot-notated routing key, e.g. `public.meal.suggestion.requested`. Set by each concrete message class.
- `lifecycle_action`
  - Type: `LifecycleAction`
  - Required: Yes
  - Default: none
  - Description: The canonical state mutation type for the entity in the payload.
- `correlation_id`
  - Type: `UUID`
  - Required: Yes
  - Default: none
  - Description: Cross-service trace identifier. Pass the same value through the full request chain.
- `organization_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: Corporate tenant boundary key. Present from Phase 1; enforces data isolation at the topic level.
- `workspace_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: Functional workspace partition key. Present from Phase 1; becomes functionally active in Phase 3.
- `actor_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The user, service, or system identity that triggered this event.
- `timestamp`
  - Type: `datetime`
  - Required: No
  - Default: `utcnow()`
  - Description: The moment the message was constructed and dispatched by the publisher.

---

### `SignalMessage[T]`

**Module:** `cynthus.messaging.common.signal.message`

The generic concrete message class. Binds `SignalMessageBase` with a typed payload via a `TypeVar` bounded to `SignalPayload`.

```python
class SignalMessage(SignalMessageBase, Generic[PayloadT]):
    payload: PayloadT
```

All domain message classes (`MealPlanCreatedMessage`, etc.) subclass `SignalMessage[TheirPayloadType]` and only override `event_type`.

**Usage pattern:**

```python
from cynthus.messaging.common import SignalMessage
from cynthus.messaging.component.meal.payload import MealPlanCreatedPayload

class MealPlanCreatedMessage(SignalMessage[MealPlanCreatedPayload]):
    event_type: str = PublicMealPlanCreatedSignal.name
```

---

## Full wire example

```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "public.meal.plan.created",
  "lifecycle_action": "created",
  "correlation_id": "f0e1d2c3-b4a5-6789-cdef-012345678901",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T14:32:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T14:32:00.000000+00:00",
    "metadata": { "execution_ms": 42 },
    "plan_id": "plan_01HXYZGHI",
    "horizon": "week",
    "start_date": "2026-06-09",
    "end_date": "2026-06-15",
    "meal_count": 14,
    "astri_assisted": true
  }
}
```
