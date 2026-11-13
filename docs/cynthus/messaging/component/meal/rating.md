# Meal Rating Signals (`public.meal.rating.*`)

User ratings provide explicit feedback on meals after they are cooked or consumed. Ratings feed `cynthus-analysis` for preference model training. A rating carries a numeric score and an optional free-text comment.

---

## `public.meal.rating.created`

**Signal class:** `PublicMealRatingCreatedSignal`
**Message class:** `MealRatingCreatedMessage`
**Payload class:** `MealRatingCreatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-analysis`

**When:** A user submits a rating for a meal entry.

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
  - Description: Moment the rating was submitted.
  - Example: `"2026-06-09T20:15:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `rating_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the created rating record.
  - Example: `"rtg_01HXYZABC"`
- `meal_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the meal that was rated.
  - Example: `"meal_01HXYZDEF"`
- `score`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: The numeric rating score. Typically 1-5.
  - Example: `4`
- `comment`
  - Type: `str | None`
  - Required: No
  - Default: `None`
  - Description: An optional free-text comment accompanying the rating.
  - Example: `"Great flavour, would make again."`

### Wire example

```json
{
  "event_id": "hhhhhhhh-8888-0000-0000-000000000001",
  "event_type": "public.meal.rating.created",
  "lifecycle_action": "created",
  "correlation_id": "iiiiiiii-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T20:15:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T20:15:00.000000+00:00",
    "metadata": {},
    "rating_id": "rtg_01HXYZABC",
    "meal_id": "meal_01HXYZDEF",
    "score": 4,
    "comment": "Great flavour, would make again."
  }
}
```

---

## `public.meal.rating.updated`

**Signal class:** `PublicMealRatingUpdatedSignal`
**Message class:** `MealRatingUpdatedMessage`
**Payload class:** `MealRatingUpdatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-analysis`

**When:** A user revises their existing rating (score, comment, or both).

**Note on `comment`:** A `null` comment means the user cleared their previous comment - it is not the same as a rating that was created without one. `cynthus-analysis` should treat this as a deletion of the prior comment text.

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
  - Description: Moment the revision was submitted.
  - Example: `"2026-06-10T08:30:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `rating_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the updated rating record.
  - Example: `"rtg_01HXYZABC"`
- `meal_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the meal the rating belongs to.
  - Example: `"meal_01HXYZDEF"`
- `score`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: The revised numeric rating score.
  - Example: `5`
- `comment`
  - Type: `str | None`
  - Required: No
  - Default: `None`
  - Description: The revised comment. `None` indicates the comment was cleared.
  - Example: `null`

### Wire example

```json
{
  "event_id": "iiiiiiii-9999-0000-0000-000000000002",
  "event_type": "public.meal.rating.updated",
  "lifecycle_action": "updated",
  "correlation_id": "iiiiiiii-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-10T08:30:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-10T08:30:00.000000+00:00",
    "metadata": {},
    "rating_id": "rtg_01HXYZABC",
    "meal_id": "meal_01HXYZDEF",
    "score": 5,
    "comment": null
  }
}
```

---

## `public.meal.rating.deleted`

**Signal class:** `PublicMealRatingDeletedSignal`
**Message class:** `MealRatingDeletedMessage`
**Payload class:** `MealRatingDeletedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-analysis`

**When:** A user removes their rating for a meal.

**Purpose:** Notifies `cynthus-analysis` to retract the rating from the preference model entirely.

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
  - Description: Moment the rating was removed.
  - Example: `"2026-06-11T09:00:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `rating_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the removed rating.
  - Example: `"rtg_01HXYZABC"`
- `meal_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the meal the rating was removed from.
  - Example: `"meal_01HXYZDEF"`

### Wire example

```json
{
  "event_id": "jjjjjjjj-aaaa-0000-0000-000000000003",
  "event_type": "public.meal.rating.deleted",
  "lifecycle_action": "deleted",
  "correlation_id": "iiiiiiii-0000-0000-0000-000000000002",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-11T09:00:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-11T09:00:00.000000+00:00",
    "metadata": {},
    "rating_id": "rtg_01HXYZABC",
    "meal_id": "meal_01HXYZDEF"
  }
}
```
