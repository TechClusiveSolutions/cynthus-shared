# Inventory Location Signals (`public.inventory.location.*`)

A location is a named physical storage space such as a pantry, fridge or freezer.

---

## `public.inventory.location.created`

**Signal class:** `PublicInventoryLocationCreatedSignal`
**Message class:** `InventoryLocationCreatedMessage`
**Payload class:** `InventoryLocationCreatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A new inventory location is created. Lets `cynthus-core-cache` and `cynthus-audit` record the new location.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `location_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the location.
- `name`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The name of the location.
- `type`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The kind of storage space, for example ambient, fridge or freezer.

Set the envelope `lifecycle_action` to `created`.

### Wire example

```json
{
  "event_type": "public.inventory.location.created",
  "lifecycle_action": "created",
  "payload": {
    "schema_version": 1,
    "location_id": "example",
    "name": "example",
    "type": "example"
  }
}
```

---

## `public.inventory.location.updated`

**Signal class:** `PublicInventoryLocationUpdatedSignal`
**Message class:** `InventoryLocationUpdatedMessage`
**Payload class:** `InventoryLocationUpdatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-audit`

**When:** A location's metadata changes. Lets `cynthus-core-cache` and `cynthus-audit` refresh the location.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
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
- `type`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The new storage type, when it changed.
- `archived`
  - Type: `Optional[bool]`
  - Required: No
  - Default: `None`
  - Description: Whether the location is now archived, when that changed.

Set the envelope `lifecycle_action` to `updated`.

### Wire example

```json
{
  "event_type": "public.inventory.location.updated",
  "lifecycle_action": "updated",
  "payload": {
    "schema_version": 1,
    "location_id": "example",
    "name": "example",
    "type": "example",
    "archived": true
  }
}
```

---

## `public.inventory.location.deleted`

**Signal class:** `PublicInventoryLocationDeletedSignal`
**Message class:** `InventoryLocationDeletedMessage`
**Payload class:** `InventoryLocationDeletedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-shopping`, `cynthus-audit`

**When:** A location is removed. Lets `cynthus-shopping` clear procurement links and `cynthus-core-cache` drop the location.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `location_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the location.

Set the envelope `lifecycle_action` to `deleted`.

### Wire example

```json
{
  "event_type": "public.inventory.location.deleted",
  "lifecycle_action": "deleted",
  "payload": {
    "schema_version": 1,
    "location_id": "example"
  }
}
```
