# Recipe Domain Signals

The `recipe` domain covers a user's recipes: where they came from (`manual`, `web` or `image`), who owns them and the page they were imported from. The Core API asks the Recipe service to create, get, list, update or delete recipes, or to import one from a web page or an uploaded image, with a request signal and gets the answer back as a response signal, so the client is acknowledged at once. A change is followed by a fact. All are `public.*` and are published to `cynthus-events-topic`.

---

## Signals

- `public.recipe.recipe.requested`
  - Emitted by: `cynthus-core-api`
  - Purpose: Hands the request to the Recipe service so the caller gets an immediate acknowledgement.
- `public.recipe.recipe.responded`
  - Emitted by: `cynthus-recipe`
  - Purpose: Carries the outcome back to `cynthus-core-api`, which relays it to the caller.
- `public.recipe.recipe.created`
  - Emitted by: `cynthus-recipe`
  - Purpose: Lets other services know a recipe exists and where it came from.
- `public.recipe.recipe.updated`
  - Emitted by: `cynthus-recipe`
  - Purpose: Lets other services know which fields of a recipe changed.
- `public.recipe.recipe.deleted`
  - Emitted by: `cynthus-recipe`
  - Purpose: Lets other services drop what they hold for the recipe.

---

## `public.recipe.recipe.requested`

**Signal class:** `PublicRecipeRecipeRequestedSignal`
**Message class:** `RecipeRequestedMessage`
**Payload class:** `RecipeRequestedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-recipe`

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `operation`
  - Type: `Literal['create', 'get', 'list', 'update', 'delete', 'import_url', 'import_image']`
  - Required: Yes
  - Default: none
  - Description: What to do with recipes.
- `resource_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The recipe to get, update or delete.
- `filters`
  - Type: `Dict[str, Any]`
  - Required: No
  - Default: `{}`
  - Description: Narrows a list, for example `q`, `source` or `owner`.
- `data`
  - Type: `Dict[str, Any]`
  - Required: No
  - Default: `{}`
  - Description: The fields to create or change a recipe with. For `import_url` the `url`; for `import_image` the `upload_id` the Core API parked in the cache and the `content_type`.

`get`, `list` need `recipe:read`; every other operation needs `recipe:write`.

---

## `public.recipe.recipe.responded`

**Signal class:** `PublicRecipeRecipeRespondedSignal`
**Message class:** `RecipeRespondedMessage`
**Payload class:** `RecipeRespondedPayload`

**Emitted by:** `cynthus-recipe`
**Consumed by:** `cynthus-core-api`

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
  - Description: `200`, `201` or `204` when it worked; `401`, `403`, `404`, `405`, `409`, `422`, `502` or `503` when it did not.
- `result`
  - Type: `Optional[Any]`
  - Required: No
  - Default: `None`
  - Description: The recipe, or the list of recipes, when it worked.
- `error`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: Why the request failed.

---

## `public.recipe.recipe.created`, `.updated` and `.deleted`

**Emitted by:** `cynthus-recipe` after the change is committed.

- `created`: `recipe_id`, `owner_id`, `source` (`manual`, `web` or `image`), `source_url` (optional)
- `updated`: `recipe_id`, `owner_id`, `changed` (the fields that changed)
- `deleted`: `recipe_id`, `owner_id`

All three also carry `schema_version` (default `1`).
