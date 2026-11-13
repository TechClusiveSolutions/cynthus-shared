# Meal Tag Signals (`public.meal.tag.*`)

Tags are free-form labels applied to meal entries (e.g. `"quick"`, `"comfort-food"`, `"high-protein"`). They are used by `cynthus-recipe` for preference indexing and by `cynthus-analysis` for lifestyle pattern modelling.

---

## `public.meal.tag.created`

**Signal class:** `PublicMealTagCreatedSignal`
**Message class:** `MealTagCreatedMessage`
**Payload class:** `MealTagCreatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-recipe`, `cynthus-analysis`

**When:** A tag is applied to a meal entry.

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
  - Description: Moment the tag was applied.
  - Example: `"2026-06-09T20:20:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `tag_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the created tag record.
  - Example: `"tag_01HXYZABC"`
- `meal_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the meal the tag was applied to.
  - Example: `"meal_01HXYZDEF"`
- `tag`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The tag value. No enforced normalisation at the signal layer - normalisation is the responsibility of `cynthus-recipe`.
  - Example: `"quick"`

### Wire example

```json
{
  "event_id": "kkkkkkkk-bbbb-0000-0000-000000000001",
  "event_type": "public.meal.tag.created",
  "lifecycle_action": "created",
  "correlation_id": "llllllll-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T20:20:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T20:20:00.000000+00:00",
    "metadata": {},
    "tag_id": "tag_01HXYZABC",
    "meal_id": "meal_01HXYZDEF",
    "tag": "quick"
  }
}
```

---

## `public.meal.tag.deleted`

**Signal class:** `PublicMealTagDeletedSignal`
**Message class:** `MealTagDeletedMessage`
**Payload class:** `MealTagDeletedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-recipe`, `cynthus-analysis`

**When:** A tag is removed from a meal entry.

**Purpose:** Notifies `cynthus-recipe` and `cynthus-analysis` to remove the tag from their preference indexes. The `meal_id` is included so consumers can invalidate tag-indexed lookup caches without a separate fetch.

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
  - Description: Moment the tag was removed.
  - Example: `"2026-06-10T10:00:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `tag_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the removed tag record.
  - Example: `"tag_01HXYZABC"`
- `meal_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the meal the tag was removed from.
  - Example: `"meal_01HXYZDEF"`

### Wire example

```json
{
  "event_id": "mmmmmmmm-cccc-0000-0000-000000000002",
  "event_type": "public.meal.tag.deleted",
  "lifecycle_action": "deleted",
  "correlation_id": "llllllll-0000-0000-0000-000000000002",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-10T10:00:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-10T10:00:00.000000+00:00",
    "metadata": {},
    "tag_id": "tag_01HXYZABC",
    "meal_id": "meal_01HXYZDEF"
  }
}
```
