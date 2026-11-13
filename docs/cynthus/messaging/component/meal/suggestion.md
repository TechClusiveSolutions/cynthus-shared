# Meal Suggestion Signals (`public.meal.suggestion.*`)

See [index.md](index.md) for the full suggestion lifecycle flow and key design constraints.

---

## `public.meal.suggestion.requested`

**Signal class:** `PublicMealSuggestionRequestedSignal`
**Message class:** `MealSuggestionRequestedMessage`
**Payload class:** `MealSuggestionRequestedPayload`

**Emitted by:** `cynthus-core-api`

**When:** A user initiates an on-demand meal suggestion, or the scheduler triggers a scheduled suggestion delivery.

**Purpose:** Acts as the starting gate for the suggestion lifecycle. Carries the `context_bundle_id` that will be the correlation anchor for all downstream signals in this suggestion round. The full context bundle is forwarded to `cynthus-chat` via VNet peering - not via this signal.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: Payload schema version. Must be `>= 1`.
  - Example: `1`
- `observed_at`
  - Type: `datetime`
  - Required: No
  - Default: `utcnow()`
  - Description: Moment the request was observed at the edge.
  - Example: `"2026-06-09T14:32:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{"source": "mobile_app"}`
- `context_bundle_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier minted by `cynthus-core-api` for the assembled context bundle. This ID links all signals in this suggestion round.
  - Example: `"cb_01HXYZABC"`
- `trigger`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: What initiated the suggestion.
  - Example: `"on_demand"` or `"scheduled"`
- `energy_level`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: The user's current Energy Banker spoon budget at the time of request.
  - Example: `7`

### Wire example

```json
{
  "event_id": "11111111-0000-0000-0000-000000000001",
  "event_type": "public.meal.suggestion.requested",
  "lifecycle_action": "created",
  "correlation_id": "aaaaaaaa-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T14:32:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T14:32:00.000000+00:00",
    "metadata": {},
    "context_bundle_id": "cb_01HXYZABC",
    "trigger": "on_demand",
    "energy_level": 7
  }
}
```

---

## `public.meal.suggestion.generated`

**Signal class:** `PublicMealSuggestionGeneratedSignal`
**Message class:** `MealSuggestionGeneratedMessage`
**Payload class:** `MealSuggestionGeneratedPayload`

**Emitted by:** `cynthus-chat`

**When:** Astri produces a meal suggestion and begins streaming the response back to the user.

**Purpose:** Notifies `cynthus-core-api` and `cynthus-analysis` that a suggestion was produced. The payload carries only IDs - all rich detail (meal name, recipe IDs, rationale, spoon cost, estimated cost) was persisted to `cynthus-intel-db` by `cynthus-chat` when the suggestion was generated. Downstream consumers resolve detail by looking up `suggestion_id` in Intel DB.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: Payload schema version.
  - Example: `1`
- `observed_at`
  - Type: `datetime`
  - Required: No
  - Default: `utcnow()`
  - Description: Moment the suggestion was generated.
  - Example: `"2026-06-09T14:32:01.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{"model_version": "astri-v1.0"}`
- `suggestion_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the generated suggestion record in `cynthus-intel-db`.
  - Example: `"sug_01HXYZGHI"`
- `context_bundle_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The context bundle identifier from the originating `requested` signal. Correlates this signal to the full suggestion round.
  - Example: `"cb_01HXYZABC"`

### Wire example

```json
{
  "event_id": "22222222-0000-0000-0000-000000000002",
  "event_type": "public.meal.suggestion.generated",
  "lifecycle_action": "created",
  "correlation_id": "aaaaaaaa-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "svc_cynthus-chat",
  "timestamp": "2026-06-09T14:32:01.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T14:32:01.000000+00:00",
    "metadata": {},
    "suggestion_id": "sug_01HXYZGHI",
    "context_bundle_id": "cb_01HXYZABC"
  }
}
```

---

## `public.meal.suggestion.accepted`

**Signal class:** `PublicMealSuggestionAcceptedSignal`
**Message class:** `MealSuggestionAcceptedMessage`
**Payload class:** `MealSuggestionAcceptedPayload`

**Emitted by:** `cynthus-core-api`

**When:** A user accepts the meal suggestion presented by Astri.

**Purpose:** Signals acceptance for preference model training in `cynthus-analysis`. The payload carries only IDs - `cynthus-analysis` resolves the full suggestion detail (which recipes were considered, what constraints were active, what the energy level was) from `cynthus-intel-db` using the provided IDs.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: Payload schema version.
  - Example: `1`
- `observed_at`
  - Type: `datetime`
  - Required: No
  - Default: `utcnow()`
  - Description: Moment acceptance was recorded.
  - Example: `"2026-06-09T14:33:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `suggestion_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the accepted suggestion in `cynthus-intel-db`.
  - Example: `"sug_01HXYZGHI"`
- `context_bundle_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The context bundle identifier. Allows `cynthus-analysis` to correlate acceptance to the full snapshot that produced this suggestion (constraints, inventory state, energy level, trigger).
  - Example: `"cb_01HXYZABC"`

### Wire example

```json
{
  "event_id": "33333333-0000-0000-0000-000000000003",
  "event_type": "public.meal.suggestion.accepted",
  "lifecycle_action": "updated",
  "correlation_id": "aaaaaaaa-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T14:33:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T14:33:00.000000+00:00",
    "metadata": {},
    "suggestion_id": "sug_01HXYZGHI",
    "context_bundle_id": "cb_01HXYZABC"
  }
}
```

---

## `public.meal.suggestion.rejected`

**Signal class:** `PublicMealSuggestionRejectedSignal`
**Message class:** `MealSuggestionRejectedMessage`
**Payload class:** `MealSuggestionRejectedPayload`

**Emitted by:** `cynthus-core-api`

**When:** A user rejects the meal suggestion presented by Astri, with or without providing a reason.

**Purpose:** Triggers a new suggestion round via `cynthus-core-api`, and feeds rejection data to `cynthus-analysis` for preference model training. The `reason` field is optional - users frequently decline without explanation. `cynthus-analysis` can still build patterns from silent rejections by correlating `context_bundle_id` to the snapshot (e.g. consistently rejecting high-spoon-cost suggestions in morning sessions, even without a stated reason).

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: Payload schema version.
  - Example: `1`
- `observed_at`
  - Type: `datetime`
  - Required: No
  - Default: `utcnow()`
  - Description: Moment rejection was recorded.
  - Example: `"2026-06-09T14:32:45.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `suggestion_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the rejected suggestion in `cynthus-intel-db`.
  - Example: `"sug_01HXYZGHI"`
- `context_bundle_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The context bundle identifier. Allows `cynthus-analysis` to correlate rejection to the full context snapshot.
  - Example: `"cb_01HXYZABC"`
- `reason`
  - Type: `str | None`
  - Required: No
  - Default: `None`
  - Description: The user's stated reason for rejection. `None` when the user declines without explanation - this is the common case and must be handled.
  - Example: `"Not in the mood for pasta"`

### Wire example - with reason

```json
{
  "event_id": "44444444-0000-0000-0000-000000000004",
  "event_type": "public.meal.suggestion.rejected",
  "lifecycle_action": "updated",
  "correlation_id": "aaaaaaaa-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T14:32:45.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T14:32:45.000000+00:00",
    "metadata": {},
    "suggestion_id": "sug_01HXYZGHI",
    "context_bundle_id": "cb_01HXYZABC",
    "reason": "Not in the mood for pasta"
  }
}
```

### Wire example - silent rejection

```json
{
  "event_id": "55555555-0000-0000-0000-000000000005",
  "event_type": "public.meal.suggestion.rejected",
  "lifecycle_action": "updated",
  "correlation_id": "bbbbbbbb-0000-0000-0000-000000000002",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T15:10:12.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T15:10:12.000000+00:00",
    "metadata": {},
    "suggestion_id": "sug_01HXYZJKL",
    "context_bundle_id": "cb_01HXYZDEF",
    "reason": null
  }
}
```

---

## Context bundle

The `context_bundle_id` referenced in these signals points to a structured record persisted in `cynthus-intel-db` by `cynthus-chat` at the moment of suggestion generation. The bundle is never stored in Core services and is never transmitted over the public bus.

**Contents of the context bundle:**

- Profile snapshot
  - Source service: `cynthus-profile`
  - Contents: Hard constraints (allergens, dietary restrictions, medication restrictions), soft preferences (cuisines, portion size, dietary style), `energy_level` at time of request
- Inventory snapshot
  - Source service: `cynthus-inventory`
  - Contents: Items available, quantities, expiry dates - scoped to items relevant to the filtered recipe candidates
- Recipe candidates
  - Source service: `cynthus-recipe`
  - Contents: Constraint-filtered list: recipe IDs, names, estimated spoon costs, estimated costs USD
- Request metadata
  - Source service: `cynthus-core-api`
  - Contents: `trigger`, `request_timestamp`, `session_id`

Open-source services see `context_bundle_id` as an opaque string. Only closed-source Intelligence subnet services (`cynthus-chat`, `cynthus-analysis`) can resolve it - both share access to `cynthus-intel-db` within the private VNet.
