# Partner Service List Signals (`public.partner.service_list.*`)

A caller asks for the list of services offered by partners. The Core API publishes a `requested` signal and relays the matching `responded` signal to the caller, joined by the envelope `correlation_id`.

---

## `public.partner.service_list.requested`

**Signal class:** `PublicPartnerServiceListRequestedSignal`
**Message class:** `PartnerServiceListRequestedMessage`
**Payload class:** `PartnerServiceListRequestedPayload`

**Emitted by:** `cynthus-core-api`
**Consumed by:** `cynthus-partner-api`

**When:** A caller asks for the list of partner services. The caller can narrow the list with filters.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `filters`
  - Type: `PartnerServiceListFilters`
  - Required: No
  - Default: empty filters
  - Description: Narrows the list.

`PartnerServiceListFilters` refuses keys it does not know.

- `name`
  - Type: `str`
  - Required: No
  - Default: `None`
  - Description: Optional; case-insensitive contains. With no name, all partners are returned.

### Wire example

```json
{
  "event_type": "public.partner.service_list.requested",
  "payload": {
    "schema_version": 1,
    "filters": { "name": "acme" }
  }
}
```

---

## `public.partner.service_list.responded`

**Signal class:** `PublicPartnerServiceListRespondedSignal`
**Message class:** `PartnerServiceListRespondedMessage`
**Payload class:** `PartnerServiceListRespondedPayload`

**Emitted by:** `cynthus-partner-api`
**Consumed by:** `cynthus-core-api`

**When:** The Partner service has dealt with a request for the service list. It carries the outcome back to `cynthus-core-api`, which relays it to the caller.

### Payload fields

- `schema_version`
  - Type: `int`
  - Required: No
  - Default: `1`
  - Description: Payload schema version.
- `status`
  - Type: `int`
  - Required: Yes
  - Default: none
  - Description: `200` when it worked; `401`, `403` or `422` when it did not. The type is not range checked.
- `result`
  - Type: `list[PartnerServiceListItem]`
  - Required: No
  - Default: `None`
  - Description: The services, when it worked.
- `error`
  - Type: `str`
  - Required: No
  - Default: `None`
  - Description: Why the request failed.

`PartnerServiceListItem` holds one service.

- `id`
  - Type: `UUID`
  - Required: Yes
  - Default: none
  - Description: The identifier of the service.
- `name`
  - Type: `str`
  - Required: Yes
  - Default: none
  - Description: The name of the service.

### Wire example

```json
{
  "event_type": "public.partner.service_list.responded",
  "payload": {
    "schema_version": 1,
    "status": 200,
    "result": [
      { "id": "0b0f6a0e-6c0a-4c55-9a53-7d1f4a6a1c11", "name": "Acme Delivery" }
    ]
  }
}
```
