# Inventory Item Signals (`public.inventory.item.*`)

An item is a quantity of a product held on a shelf.

---

## `public.inventory.item.added`

**Signal class:** `PublicInventoryItemAddedSignal`
**Message class:** `InventoryItemAddedMessage`
**Payload class:** `InventoryItemAddedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-scheduler`, `cynthus-audit`

**When:** An item is added to a shelf. Lets `cynthus-core-cache` update the snapshot and `cynthus-scheduler` register an expiry watch.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `item_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the item.
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
  - Description: The name of the item.
- `quantity`
  - Type: `float`
  - Required: Yes
  - Default: none
  - Description: The quantity on hand.
- `unit`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The unit of measure, for example gallon.
- `low_threshold`
  - Type: `Optional[float]`
  - Required: No
  - Default: `None`
  - Description: The quantity below which the item counts as low.
- `expiry_date`
  - Type: `Optional[date]`
  - Required: No
  - Default: `None`
  - Description: The date the item expires.
- `barcode`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The barcode of the item.
- `catalog_item_id`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The catalog entry the item was matched to.

Set the envelope `lifecycle_action` to `created`.

### Wire example

```json
{
  "event_type": "public.inventory.item.added",
  "lifecycle_action": "created",
  "payload": {
    "schema_version": 1,
    "item_id": "example",
    "shelf_id": "example",
    "location_id": "example",
    "name": "example",
    "quantity": 1.5,
    "unit": "example",
    "low_threshold": 1.5,
    "expiry_date": "2027-04-17",
    "barcode": "example",
    "catalog_item_id": "example"
  }
}
```

---

## `public.inventory.item.updated`

**Signal class:** `PublicInventoryItemUpdatedSignal`
**Message class:** `InventoryItemUpdatedMessage`
**Payload class:** `InventoryItemUpdatedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-scheduler`, `cynthus-audit`

**When:** An item's quantity or metadata changes. Lets `cynthus-core-cache` and `cynthus-scheduler` refresh the item and its expiry watch.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `item_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the item.
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
- `quantity`
  - Type: `Optional[float]`
  - Required: No
  - Default: `None`
  - Description: The new quantity, when it changed.
- `unit`
  - Type: `Optional[str]`
  - Required: No
  - Default: `None`
  - Description: The new unit, when it changed.
- `low_threshold`
  - Type: `Optional[float]`
  - Required: No
  - Default: `None`
  - Description: The new low threshold, when it changed.
- `expiry_date`
  - Type: `Optional[date]`
  - Required: No
  - Default: `None`
  - Description: The new expiry date, when it changed.

Set the envelope `lifecycle_action` to `updated`.

### Wire example

```json
{
  "event_type": "public.inventory.item.updated",
  "lifecycle_action": "updated",
  "payload": {
    "schema_version": 1,
    "item_id": "example",
    "shelf_id": "example",
    "location_id": "example",
    "name": "example",
    "quantity": 1.5,
    "unit": "example",
    "low_threshold": 1.5,
    "expiry_date": "2027-04-17"
  }
}
```

---

## `public.inventory.item.removed`

**Signal class:** `PublicInventoryItemRemovedSignal`
**Message class:** `InventoryItemRemovedMessage`
**Payload class:** `InventoryItemRemovedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-core-cache`, `cynthus-scheduler`, `cynthus-audit`

**When:** An item is removed from a shelf. Lets `cynthus-core-cache` drop the item and `cynthus-scheduler` cancel its expiry watch.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `item_id`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The identifier of the item.
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
  "event_type": "public.inventory.item.removed",
  "lifecycle_action": "deleted",
  "payload": {
    "schema_version": 1,
    "item_id": "example",
    "shelf_id": "example",
    "location_id": "example"
  }
}
```
