# Meal Plan Signals (`public.meal.plan.*`)

A **meal plan** is a workspace-scoped schedule of meals across a defined horizon (week or month). Plans may be assembled manually or with Astri's assistance.

---

## `public.meal.plan.created`

**Signal class:** `PublicMealPlanCreatedSignal`
**Message class:** `MealPlanCreatedMessage`
**Payload class:** `MealPlanCreatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-analysis`, `cynthus-scheduler`

**When:** A new meal plan is persisted for a workspace.

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
  - Description: Moment the plan was created.
  - Example: `"2026-06-09T09:00:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `plan_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the created meal plan.
  - Example: `"plan_01HXYZABC"`
- `horizon`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The planning horizon.
  - Example: `"week"` or `"month"`
- `start_date`
  - Type: `date`
  - Required: Yes
  - Default: none
  - Description: The first date covered by the plan (ISO 8601).
  - Example: `"2026-06-09"`
- `end_date`
  - Type: `date`
  - Required: Yes
  - Default: none
  - Description: The last date covered by the plan (ISO 8601).
  - Example: `"2026-06-15"`
- `meal_count`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: The number of meals scheduled within the plan.
  - Example: `14`
- `astri_assisted`
  - Type: `bool`
  - Required: Yes
  - Default: none
  - Description: Whether Astri assisted in assembling the plan.
  - Example: `true`

### Wire example

```json
{
  "event_id": "aaaaaaaa-1111-0000-0000-000000000001",
  "event_type": "public.meal.plan.created",
  "lifecycle_action": "created",
  "correlation_id": "cccccccc-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T09:00:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T09:00:00.000000+00:00",
    "metadata": {},
    "plan_id": "plan_01HXYZABC",
    "horizon": "week",
    "start_date": "2026-06-09",
    "end_date": "2026-06-15",
    "meal_count": 14,
    "astri_assisted": true
  }
}
```

---

## `public.meal.plan.updated`

**Signal class:** `PublicMealPlanUpdatedSignal`
**Message class:** `MealPlanUpdatedMessage`
**Payload class:** `MealPlanUpdatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-analysis`, `cynthus-scheduler`

**When:** An existing meal plan is modified (e.g. meals added, removed, or rescheduled).

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
  - Description: Moment the update occurred.
  - Example: `"2026-06-10T11:15:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `plan_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the modified meal plan.
  - Example: `"plan_01HXYZABC"`
- `updated_fields`
  - Type: `list[str]`
  - Required: Yes
  - Default: none
  - Description: The names of the plan attributes that changed. Consumers use this to decide whether to invalidate cached state.
  - Example: `["meal_count", "end_date"]`

### Wire example

```json
{
  "event_id": "bbbbbbbb-2222-0000-0000-000000000002",
  "event_type": "public.meal.plan.updated",
  "lifecycle_action": "updated",
  "correlation_id": "cccccccc-0000-0000-0000-000000000002",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-10T11:15:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-10T11:15:00.000000+00:00",
    "metadata": {},
    "plan_id": "plan_01HXYZABC",
    "updated_fields": ["meal_count", "end_date"]
  }
}
```

---

## `public.meal.plan.deleted`

**Signal class:** `PublicMealPlanDeletedSignal`
**Message class:** `MealPlanDeletedMessage`
**Payload class:** `MealPlanDeletedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-analysis`, `cynthus-scheduler`

**When:** A meal plan is removed from a workspace.

**Purpose:** Instructs `cynthus-scheduler` to drop any scheduled suggestion deliveries associated with the plan, and notifies `cynthus-analysis` to evict the plan from its working state.

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
  - Description: Moment the deletion occurred.
  - Example: `"2026-06-11T08:00:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `plan_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the removed meal plan.
  - Example: `"plan_01HXYZABC"`

### Wire example

```json
{
  "event_id": "cccccccc-3333-0000-0000-000000000003",
  "event_type": "public.meal.plan.deleted",
  "lifecycle_action": "deleted",
  "correlation_id": "cccccccc-0000-0000-0000-000000000003",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-11T08:00:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-11T08:00:00.000000+00:00",
    "metadata": {},
    "plan_id": "plan_01HXYZABC"
  }
}
```
