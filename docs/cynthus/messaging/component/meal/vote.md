# Meal Vote Signals (`public.meal.vote.*`)

Group meal voting allows workspace members to collectively choose from proposed meal options. A vote session progresses through `initiated -> cast (xN) -> resolved` or is short-circuited by Astri via `auto_resolved` when a stalemate is detected.

---

## Vote lifecycle

1. `cynthus-core-api` publishes `public.meal.vote.initiated`.
2. Members cast votes, one per member. Each vote makes `cynthus-core-api` publish `public.meal.vote.cast`.
3. The vote closes when the deadline is reached or the vote is unanimous.
4. Then one of two things happens:
   - A winner is determined: `cynthus-core-api` publishes `public.meal.vote.resolved`.
   - Stalemate: `cynthus-chat` (Astri) publishes `public.meal.vote.auto_resolved`.

---

## `public.meal.vote.initiated`

**Signal class:** `PublicMealVoteInitiatedSignal`
**Message class:** `MealVoteInitiatedMessage`
**Payload class:** `MealVoteInitiatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-messaging`, `cynthus-notification`, `cynthus-analysis`

**When:** A group meal vote is opened for a workspace.

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
  - Description: Moment the vote was opened.
  - Example: `"2026-06-09T17:00:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `vote_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the vote session.
  - Example: `"vote_01HXYZABC"`
- `group_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the group this vote belongs to.
  - Example: `"grp_01HXYZ123"`
- `proposed_meal`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The display name of the proposed meal.
  - Example: `"Chicken Stir Fry"`
- `recipe_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the recipe backing the proposed meal.
  - Example: `"rcp_01HXYZDEF"`
- `expires_at`
  - Type: `datetime`
  - Required: Yes
  - Default: none
  - Description: The moment the vote closes. Serialised as ISO 8601 UTC.
  - Example: `"2026-06-09T17:30:00.000000+00:00"`

**Serialisation note:** `expires_at` is serialised by a `@field_serializer` that enforces UTC - even if a non-UTC `datetime` is provided at construction, the serialised form will always be UTC.

### Wire example

```json
{
  "event_id": "dddddddd-4444-0000-0000-000000000001",
  "event_type": "public.meal.vote.initiated",
  "lifecycle_action": "created",
  "correlation_id": "eeeeeeee-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZDEF",
  "timestamp": "2026-06-09T17:00:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T17:00:00.000000+00:00",
    "metadata": {},
    "vote_id": "vote_01HXYZABC",
    "group_id": "grp_01HXYZ123",
    "proposed_meal": "Chicken Stir Fry",
    "recipe_id": "rcp_01HXYZDEF",
    "expires_at": "2026-06-09T17:30:00.000000+00:00"
  }
}
```

---

## `public.meal.vote.cast`

**Signal class:** `PublicMealVoteCastSignal`
**Message class:** `MealVoteCastMessage`
**Payload class:** `MealVoteCastPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-analysis`, `cynthus-messaging`

**When:** A group member submits their vote on the proposed meal.

**Purpose:** Updates the running tally for `cynthus-analysis` and `cynthus-messaging`. The `current_tally` snapshot allows consumers to compute the current state without needing to aggregate all prior `cast` events.

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
  - Description: Moment the vote was cast.
  - Example: `"2026-06-09T17:05:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `vote_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the vote session.
  - Example: `"vote_01HXYZABC"`
- `group_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the group this vote belongs to.
  - Example: `"grp_01HXYZ123"`
- `vote`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The voter's submitted choice.
  - Example: `"yes"`, `"no"`, or `"pending"`
- `current_tally`
  - Type: `dict[str, int]`
  - Required: Yes
  - Default: none
  - Description: Running tally of all votes by choice at the moment this vote was cast. Consumers should use this snapshot rather than accumulating totals across events.
  - Example: `{"yes": 2, "no": 1, "pending": 1}`

### Wire example

```json
{
  "event_id": "eeeeeeee-5555-0000-0000-000000000002",
  "event_type": "public.meal.vote.cast",
  "lifecycle_action": "updated",
  "correlation_id": "eeeeeeee-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "usr_01HXYZGHI",
  "timestamp": "2026-06-09T17:05:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T17:05:00.000000+00:00",
    "metadata": {},
    "vote_id": "vote_01HXYZABC",
    "group_id": "grp_01HXYZ123",
    "vote": "yes",
    "current_tally": {"yes": 2, "no": 1, "pending": 1}
  }
}
```

---

## `public.meal.vote.resolved`

**Signal class:** `PublicMealVoteResolvedSignal`
**Message class:** `MealVoteResolvedMessage`
**Payload class:** `MealVoteResolvedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-chat`, `cynthus-notification`, `cynthus-analysis`

**When:** A group meal vote concludes with a clear winning choice (majority or unanimous).

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
  - Description: Moment the vote was resolved.
  - Example: `"2026-06-09T17:30:00.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `vote_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the concluded vote session.
  - Example: `"vote_01HXYZABC"`
- `group_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the group this vote belongs to.
  - Example: `"grp_01HXYZ123"`
- `resolution`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The display name of the winning meal choice.
  - Example: `"Chicken Stir Fry"`
- `recipe_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the recipe backing the winning choice.
  - Example: `"rcp_01HXYZDEF"`

### Wire example

```json
{
  "event_id": "ffffffff-6666-0000-0000-000000000003",
  "event_type": "public.meal.vote.resolved",
  "lifecycle_action": "updated",
  "correlation_id": "eeeeeeee-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "svc_cynthus-core-api",
  "timestamp": "2026-06-09T17:30:00.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T17:30:00.000000+00:00",
    "metadata": {},
    "vote_id": "vote_01HXYZABC",
    "group_id": "grp_01HXYZ123",
    "resolution": "Chicken Stir Fry",
    "recipe_id": "rcp_01HXYZDEF"
  }
}
```

---

## `public.meal.vote.auto_resolved`

**Signal class:** `PublicMealVoteAutoResolvedSignal`
**Message class:** `MealVoteAutoResolvedMessage`
**Payload class:** `MealVoteAutoResolvedPayload`

**Emitted by:** `cynthus-chat`
**Consumed by:** `cynthus-core-api`, `cynthus-notification`, `cynthus-analysis`

**When:** A vote reaches its deadline in a stalemate (tied or insufficient participation) and Astri acts as impartial tiebreaker.

**Purpose:** Distinguished from `vote.resolved` by both the `auto_resolved` action and the `resolved_by` and `tiebreak_rationale` fields, which provide transparency into Astri's decision. `cynthus-notification` uses `tiebreak_rationale` to communicate Astri's reasoning to group members.

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
  - Description: Moment Astri resolved the stalemate.
  - Example: `"2026-06-09T17:30:05.000000+00:00"`
- `metadata`
  - Type: `dict`
  - Required: No
  - Default: `{}`
  - Description: Non-PII operational telemetry.
  - Example: `{}`
- `vote_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the stalemated vote session.
  - Example: `"vote_01HXYZABC"`
- `group_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the group this vote belongs to.
  - Example: `"grp_01HXYZ123"`
- `resolution`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The display name of the meal Astri selected.
  - Example: `"Chicken Stir Fry"`
- `recipe_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the recipe backing Astri's selection.
  - Example: `"rcp_01HXYZDEF"`
- `tiebreak_rationale`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: Astri's explanation for the tiebreak decision. Displayed to group members via `cynthus-notification`.
  - Example: `"Chosen because it uses ingredients expiring today and matches everyone's hard constraints."`
- `resolved_by`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identity of the resolving actor.
  - Example: `"astri"`

### Wire example

```json
{
  "event_id": "gggggggg-7777-0000-0000-000000000004",
  "event_type": "public.meal.vote.auto_resolved",
  "lifecycle_action": "updated",
  "correlation_id": "eeeeeeee-0000-0000-0000-000000000001",
  "organization_id": "org_01HXYZABC",
  "workspace_id": "ws_01HXYZ123",
  "actor_id": "svc_cynthus-chat",
  "timestamp": "2026-06-09T17:30:05.000000+00:00",
  "payload": {
    "schema_version": 1,
    "observed_at": "2026-06-09T17:30:05.000000+00:00",
    "metadata": {},
    "vote_id": "vote_01HXYZABC",
    "group_id": "grp_01HXYZ123",
    "resolution": "Chicken Stir Fry",
    "recipe_id": "rcp_01HXYZDEF",
    "tiebreak_rationale": "Chosen because it uses ingredients expiring today and matches everyone's hard constraints.",
    "resolved_by": "astri"
  }
}
```
