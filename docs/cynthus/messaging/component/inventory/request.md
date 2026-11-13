# Inventory Request and Response Signals

Every request to change or read inventory records travels as a signal, so the caller gets an immediate acknowledgement and the answer arrives asynchronously. The Core API publishes a `requested` signal and relays the matching `responded` signal to the caller, joined by the envelope `correlation_id`.

- `location`
  - Request: `public.inventory.location.requested`
  - Response: `public.inventory.location.responded`
- `shelf`
  - Request: `public.inventory.shelf.requested`
  - Response: `public.inventory.shelf.responded`
- `item`
  - Request: `public.inventory.item.requested`
  - Response: `public.inventory.item.responded`
- `owner`
  - Request: `public.inventory.owner.requested`
  - Response: `public.inventory.owner.responded`

Emitted by: the request by `cynthus-core-api`, the response by `cynthus-inventory`. Both carry the caller's `organization_id`, `workspace_id` and `actor_id`. The request travels with the caller's access token in the `authorization` message property, and the Inventory service refuses a request whose token is not genuine, lacks the permission, or names another caller.

---

## Request payload

`InventoryRequestedPayload` is shared by the four request signals.

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `operation`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: `create`, `get`, `list`, `update` or `delete`.
- `resource_id`
  - Type: `str`
  - Required: No
  - Default: `None`
  - Description: The record to get, update or delete.
- `parent_id`
  - Type: `str`
  - Required: No
  - Default: `None`
  - Description: The shelf an owner belongs to.
- `filters`
  - Type: `dict`
  - Required: No
  - Default: empty
  - Description: Narrows a list, for example `type`, `name`, `location_id` or `shelf_id`.
- `data`
  - Type: `dict`
  - Required: No
  - Default: empty
  - Description: The fields to create or change a record with.

Reads (`get`, `list`) need the permission `inventory:read`; `create`, `update` and `delete` need `inventory:write`. For an owner, `create` adds the user in `data.owner_id` to the shelf in `parent_id`, `list` lists the owners of that shelf, and `delete` removes the owner in `resource_id` from it.

## Response payload

`InventoryRespondedPayload` is shared by the four response signals.

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
  - Description: `200`, `201` or `204` when it worked; `401`, `403`, `404`, `409` or `422` when it did not.
- `result`
  - Type: `Any`
  - Required: No
  - Default: `None`
  - Description: The record, or the list of records, when it worked.
- `error`
  - Type: `str`
  - Required: No
  - Default: `None`
  - Description: Why it failed.

A record in another workspace is reported as `404`, never `403`.

## Wire example

```json
{
  "event_type": "public.inventory.location.requested",
  "lifecycle_action": "updated",
  "payload": {
    "schema_version": 1,
    "operation": "create",
    "data": { "name": "Chest freezer", "type": "frozen" }
  }
}
```
