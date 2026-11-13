# Inventory Shelf Signals (`public.inventory.shelf.*`)

A shelf is a subdivision of a location that holds items and has owners.

---

## `public.inventory.shelf.created`

**Signal class:** `PublicInventoryShelfCreatedSignal`
**Message class:** `InventoryShelfCreatedMessage`
**Payload class:** `InventoryShelfCreatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A new shelf is added to a location. Lets `cynthus-core-cache` and `cynthus-audit` record the new shelf.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `shelf_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shelf.
- `location_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the location.
- `name`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The name of the shelf.
- `position`
  - Type: `int`
  - Required: No
  - Default: `0`
  - Description: The position of the shelf within its location.

Set the envelope `lifecycle_action` to `created`.

### Wire example

```json
{
  "event_type": "public.inventory.shelf.created",
  "lifecycle_action": "created",
  "payload": {
    "schema_version": 1,
    "shelf_id": "example",
    "location_id": "example",
    "name": "example",
    "position": 1
  }
}
```

---

## `public.inventory.shelf.updated`

**Signal class:** `PublicInventoryShelfUpdatedSignal`
**Message class:** `InventoryShelfUpdatedMessage`
**Payload class:** `InventoryShelfUpdatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A shelf's metadata changes. Lets `cynthus-core-cache` and `cynthus-audit` refresh the shelf.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `shelf_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shelf.
- `location_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the location.
- `name`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The new name, when it changed.
- `position`
  - Type: `Optional[int]`
  - Required: No
  - Default: `None`
  - Description: The new position, when it changed.

Set the envelope `lifecycle_action` to `updated`.

### Wire example

```json
{
  "event_type": "public.inventory.shelf.updated",
  "lifecycle_action": "updated",
  "payload": {
    "schema_version": 1,
    "shelf_id": "example",
    "location_id": "example",
    "name": "example",
    "position": 1
  }
}
```

---

## `public.inventory.shelf.deleted`

**Signal class:** `PublicInventoryShelfDeletedSignal`
**Message class:** `InventoryShelfDeletedMessage`
**Payload class:** `InventoryShelfDeletedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A shelf is removed. Lets `cynthus-core-cache` drop the shelf and its items.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `shelf_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the shelf.
- `location_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the location.

Set the envelope `lifecycle_action` to `deleted`.

### Wire example

```json
{
  "event_type": "public.inventory.shelf.deleted",
  "lifecycle_action": "deleted",
  "payload": {
    "schema_version": 1,
    "shelf_id": "example",
    "location_id": "example"
  }
}
```
