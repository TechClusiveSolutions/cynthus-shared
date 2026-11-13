# Meal Recipes Signals (`public.meal.recipes.*`)

The `recipes` aggregate covers the association of one or more recipe identifiers to a composite meal entry. A single meal entry may be backed by multiple recipes (e.g. a main dish + a side dish, or multiple preparation variants).

---

## `public.meal.recipes.associated`

**Signal class:** `PublicMealRecipesAssociatedSignal`
**Message class:** `MealRecipesAssociatedMessage`
**Payload class:** `MealRecipesAssociatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-recipe`, `cynthus-analysis`

**When:** One or more recipe IDs are linked to a composite meal entry. This signal covers the full set of associations at the time of publication - it is not incremental. Consumers should treat it as the authoritative current state of the meal's recipe associations.

**Note on aggregate naming:** The aggregate is `recipes` (plural) to reflect that this signal always carries a batch - even when only one recipe is being associated.

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
  - Description: Moment the association was recorded.
  - Example: `"2026-06-09T19:00:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `meal_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the composite meal entry.
  - Example: `"meal_01HXYZDEF"`
- `recipe_ids`
  - Type: `list[str]`
  - Required: Yes
  - Default: none
  - Description: The identifiers of all recipes currently linked to the meal entry.
  - Example: `["rcp_01HXYZABC", "rcp_01HXYZDEF"]`

### Wire example

```json
{
  "event_id": "nnnnnnnn-dddd-0000-0000-000000000001",
  "event_type": "public.meal.recipes.associated",
  "lifecycle_action": "updated",
  "correlation_id": "oooooooo-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T19:00:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T19:00:00.000000+00:00",
    "metadata": {},
    "meal_id": "meal_01HXYZDEF",
    "recipe_ids": ["rcp_01HXYZABC", "rcp_01HXYZDEF"]
  }
}
```
