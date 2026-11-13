# Inventory Owner Signals (`public.inventory.owner.*`)

An owner is a user who is responsible for a shelf. These facts follow a successful owner change; asking for the change is done with the request and response signals in [request.md](request.md).

---

## `public.inventory.owner.added`

**Signal class:** `PublicInventoryOwnerAddedSignal`
**Message class:** `InventoryOwnerAddedMessage`
**Payload class:** `InventoryOwnerAddedPayload`

**Emitted by:** `cynthus-inventory`
**Consumed by:** `cynthus-audit`

**When:** A user is made an owner of a shelf. Lets subscribers see who is responsible for a shelf.

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
- `owner_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user.
- `granted_by`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The user who granted the ownership.

Set the envelope `lifecycle_action` to `created`.

### Wire example

```json
{
  "event_type": "public.inventory.owner.added",
  "lifecycle_action": "created",
  "payload": {
    "schema_version": 1,
    "shelf_id": "example",
    "owner_id": "example",
    "granted_by": "example"
  }
}
```

---

## `public.inventory.owner.removed`

**Signal class:** `PublicInventoryOwnerRemovedSignal`
**Message class:** `InventoryOwnerRemovedMessage`
**Payload class:** `InventoryOwnerRemovedPayload`

**Emitted by:** `cynthus-inventory`
**Consumed by:** `cynthus-audit`

**When:** A user stops being an owner of a shelf.

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
- `owner_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the user.

Set the envelope `lifecycle_action` to `deleted`.

### Wire example

```json
{
  "event_type": "public.inventory.owner.removed",
  "lifecycle_action": "deleted",
  "payload": {
    "schema_version": 1,
    "shelf_id": "example",
    "owner_id": "example"
  }
}
```
