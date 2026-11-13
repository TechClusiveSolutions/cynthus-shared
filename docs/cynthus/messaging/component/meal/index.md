# Meal Domain Signals

The `meal` domain covers the full lifecycle of meal planning, AI-driven suggestions, group voting, user ratings, and recipe associations. All signals in this domain are published to `cynthus-events-topic` and carry the prefix `public.meal.*`.

---

## Aggregates

- `plan`
  - Signal prefix: `public.meal.plan.*`
  - Description: Meal plans scoped to a workspace.
- `rating`
  - Signal prefix: `public.meal.rating.*`
  - Description: User ratings (score + optional comment) on a meal entry.
- `recipes`
  - Signal prefix: `public.meal.recipes.*`
  - Description: Associations between recipe IDs and a composite meal entry.
- `suggestion`
  - Signal prefix: `public.meal.suggestion.*`
  - Description: Astri's AI-driven meal suggestion lifecycle.
- `tag`
  - Signal prefix: `public.meal.tag.*`
  - Description: Free-form tags applied to meal entries for preference indexing.
- `vote`
  - Signal prefix: `public.meal.vote.*`
  - Description: Group voting on proposed meal choices.

---

## Suggestion signal flow

The suggestion lifecycle is the most important flow in the meal domain. Understanding the ordering and ownership of each signal is critical for both Core and Intelligence contributors.

1. The user starts a request.
2. `cynthus-core-api`:
   1. Mints a `context_bundle_id` (UUIDv4).
   2. Assembles the context bundle: hard constraints and soft preferences from `cynthus-profile`, an inventory snapshot from `cynthus-inventory`, and filtered recipe candidates from `cynthus-recipe`.
   3. Publishes `public.meal.suggestion.requested`.
   4. Forwards the full bundle to `cynthus-chat` over VNet peering.
3. `cynthus-chat` (Intelligence subnet, dark):
   1. Generates a suggestion from the assembled context.
   2. Persists to `cynthus-intel-db`: the context bundle (keyed by `context_bundle_id`), the suggestion record (keyed by `suggestion_id`), and the meal and recipe references.
   3. Publishes `public.meal.suggestion.generated`.
   4. Returns a streaming response to the user through `cynthus-core-api`.
4. The user responds:
   - Accepts: `cynthus-core-api` publishes `public.meal.suggestion.accepted`.
   - Rejects: `cynthus-core-api` publishes `public.meal.suggestion.rejected` and triggers a new suggestion round.

**Key design constraints:**

- `cynthus-chat` **never** calls back into Core services at runtime. The entire context it needs is delivered in the assembled bundle via VNet peering.
- All suggestion detail (meal name, recipe IDs, rationale, spoon cost) is persisted in `cynthus-intel-db` by `cynthus-chat` when the suggestion is generated. Public signals carry only IDs - downstream consumers resolve detail from Intel DB.
- `cynthus-analysis` (also in the Intelligence subnet) resolves `suggestion_id` and `context_bundle_id` against `cynthus-intel-db` directly. It never needs to call Core to build preference models.
- The `context_bundle_id` is the correlation anchor that links the full `requested -> generated -> accepted/rejected` chain, even though the bundle data itself only ever lives in Intel DB.

---

## Key consumers by signal

- `public.meal.suggestion.requested`: `cynthus-chat` (via VNet, not bus), `cynthus-audit`
- `public.meal.suggestion.generated`: `cynthus-core-api`, `cynthus-analysis`, `cynthus-notification`
- `public.meal.suggestion.accepted`: `cynthus-analysis`
- `public.meal.suggestion.rejected`: `cynthus-core-api` (triggers re-suggestion), `cynthus-analysis`
- `public.meal.plan.*`: `cynthus-analysis`, `cynthus-scheduler`
- `public.meal.vote.*`: `cynthus-analysis`, `cynthus-messaging`, `cynthus-notification`
- `public.meal.rating.*`: `cynthus-analysis`
- `public.meal.tag.*`: `cynthus-recipe`, `cynthus-analysis`
- `public.meal.recipes.*`: `cynthus-recipe`, `cynthus-analysis`
