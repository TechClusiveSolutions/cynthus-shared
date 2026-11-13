# Profile Domain Signals

The `profile` domain covers a user's profile: their allergies, likes, dislikes, favorites and medical conditions. The Core API asks the Profile service to create, get, update or delete the caller's own profile with a request signal and gets the answer back as a response signal, so the client is acknowledged at once. A change is followed by a fact, and a sign-in is followed by a snapshot for the Analysis engine.

Allergies and medical conditions are hard constraints. Before a change to them is committed, the Profile service publishes `audit.profile.hard_constraint.updated`. The request, response, fact and snapshot signals are `public.*`; the audit signal is `audit.*` and is consumed by `cynthus-audit`. All are published to `cynthus-events-topic`.

---

## Signals

- `public.profile.profile.requested`
  - Emitted by: `cynthus-core-api`
  - Purpose: Hands the request to the Profile service so the caller gets an immediate acknowledgement.
- `public.profile.profile.responded`
  - Emitted by: `cynthus-profile`
  - Purpose: Carries the outcome back to `cynthus-core-api`, which relays it to the caller.
- `public.profile.profile.created`
  - Emitted by: `cynthus-profile`
  - Purpose: Lets other services know a profile exists. It names which parts were set, not their contents.
- `public.profile.profile.updated`
  - Emitted by: `cynthus-profile`
  - Purpose: Lets other services know which parts of a profile changed, without the contents.
- `public.profile.profile.deleted`
  - Emitted by: `cynthus-profile`
  - Purpose: Lets other services drop what they hold for the profile.
- `public.profile.snapshot.published`
  - Emitted by: `cynthus-profile`
  - Purpose: Pushes the profile (allergies, likes, dislikes, favorites, conditions) to the Analysis engine, which correlates it with shopping and inventory patterns to refine meal suggestions.
- `audit.profile.hard_constraint.updated`
  - Emitted by: `cynthus-profile`
  - Purpose: Safety-critical audit record of a hard-constraint change (engineering standards section 6); consumed by `cynthus-audit`.

---

## `public.profile.profile.requested`

**Signal class:** `PublicProfileProfileRequestedSignal`
**Message class:** `ProfileRequestedMessage`
**Payload class:** `ProfileRequestedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-profile`

**When:** A caller asks to create, get, update or delete their profile. Hands the request to the Profile service so the caller gets an immediate acknowledgement.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `operation`
  - Type: `Literal['create', 'get', 'update', 'delete']`
  - Required: Yes
  - Default: none
  - Description: What to do: create, get, update or delete.
- `resource_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The profile to get, update or delete; omitted means the caller's own.
- `data`
  - Type: `Dict[str, Any]`
  - Required: No
  - Default: empty
  - Description: The fields to create or change the profile with.

Set the envelope `lifecycle_action` to `updated`.

---

## `public.profile.profile.responded`

**Signal class:** `PublicProfileProfileRespondedSignal`
**Message class:** `ProfileRespondedMessage`
**Payload class:** `ProfileRespondedPayload`

**Emitted by:** `cynthus-profile`
**Consumed by:** `cynthus-core-api`

**When:** It has dealt with a profile request. Carries the outcome back to `cynthus-core-api`, which relays it to the caller.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `operation`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The operation that was requested.
- `status`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: 200, 201 or 204 when it worked; 401, 403, 404, 409, 422 or 503 when it did not.
- `result`
  - Type: `Optional[Any]`
  - Required: No
  - Default: `None`
  - Description: The profile when it worked.
- `error`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: Why the request failed.

Set the envelope `lifecycle_action` to `updated`.

---

## `public.profile.profile.created`

**Signal class:** `PublicProfileProfileCreatedSignal`
**Message class:** `ProfileCreatedMessage`
**Payload class:** `ProfileCreatedPayload`

**Emitted by:** `cynthus-profile`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A profile is created. Lets other services know a profile exists. It names which parts were set, not their contents.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `profile_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the profile.
- `user_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user the profile belongs to.
- `changed`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: Which parts changed: display_name, allergies, likes, dislikes, favorites or conditions.

Set the envelope `lifecycle_action` to `created`.

---

## `public.profile.profile.updated`

**Signal class:** `PublicProfileProfileUpdatedSignal`
**Message class:** `ProfileUpdatedMessage`
**Payload class:** `ProfileUpdatedPayload`

**Emitted by:** `cynthus-profile`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A profile is changed. Lets other services know which parts of a profile changed, without the contents.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `profile_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the profile.
- `user_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user the profile belongs to.
- `changed`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: Which parts changed: display_name, allergies, likes, dislikes, favorites or conditions.

Set the envelope `lifecycle_action` to `updated`.

---

## `public.profile.profile.deleted`

**Signal class:** `PublicProfileProfileDeletedSignal`
**Message class:** `ProfileDeletedMessage`
**Payload class:** `ProfileDeletedPayload`

**Emitted by:** `cynthus-profile`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A profile is deleted. Lets other services drop what they hold for the profile.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `profile_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the profile.
- `user_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user the profile belongs to.
- `changed`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: Which parts changed: display_name, allergies, likes, dislikes, favorites or conditions.

Set the envelope `lifecycle_action` to `deleted`.

---

## `public.profile.snapshot.published`

**Signal class:** `PublicProfileSnapshotPublishedSignal`
**Message class:** `ProfileSnapshotPublishedMessage`
**Payload class:** `ProfileSnapshotPublishedPayload`

**Emitted by:** `cynthus-profile`
**Consumed by:** `cynthus-analysis`

**When:** A user signs in and has a profile. Pushes the profile (allergies, likes, dislikes, favorites, conditions) to the Analysis engine, which correlates it with shopping and inventory patterns to refine meal suggestions.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `user_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user the profile belongs to.
- `profile`
  - Type: `Dict[str, Any]`
  - Required: Yes
  - Default: none
  - Description: The whole profile as the Profile service returns it.
- `reason`
  - Type: `str`
  - Required: No
  - Default: `'authentication'`
  - Description: Why the snapshot was published.

Set the envelope `lifecycle_action` to `snapshot`.

---

## `audit.profile.hard_constraint.updated`

**Signal class:** `AuditProfileHardConstraintUpdatedSignal`
**Message class:** `ProfileHardConstraintUpdatedMessage`
**Payload class:** `ProfileHardConstraintUpdatedPayload`

**Emitted by:** `cynthus-profile`
**Consumed by:** `cynthus-audit`

**When:** Allergies or medical conditions are about to change (published before the change is committed). Safety-critical audit record of a hard-constraint change (engineering standards section 6); consumed by `cynthus-audit`.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `user_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user the profile belongs to.
- `profile_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the profile.
- `kind`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: allergy or condition.
- `added`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: The entries being added.
- `removed`
  - Type: `List[str]`
  - Required: No
  - Default: empty list
  - Description: The entries being removed.

Set the envelope `lifecycle_action` to `updated`.

---

## Operations and statuses

A request names an `operation`; `data` is what the Profile service reads.

- `create`
  - `data`: `display_name` and the lists `allergies`, `likes`, `dislikes`, `favorites`, `conditions`; each entry is a name or `{name, detail}`
  - Answer: `201` and the profile; `409` if the user already has one
- `get`
  - `data`: none
  - Answer: `200` and the profile; `404` if there is none
- `update`
  - `data`: `display_name`, and per list either a replacement list or `{set, add, remove}`
  - Answer: `200` and the profile
- `delete`
  - `data`: none
  - Answer: `204`

Every operation applies to the caller's own profile; a profile is never reached by anyone else. `get` needs `profile:read`, the rest need `profile:write`. Other statuses: `401` (token missing, forged or for another caller), `403` (token lacks the permission), `422` (input rejected), `503` (the audit signal for a hard-constraint change could not be published, so nothing was changed).
