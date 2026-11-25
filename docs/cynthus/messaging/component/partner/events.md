# Partner Events

The partner events are `SignalEvent` classes in `cynthus.core.event`. Both are reads, so `PartnerEvent` allows only the
action `RETRIEVED`; any other action is refused when the event is created. Their data models are small classes of their
own, because `cynthus.core` does not import `cynthus.messaging`. Every data model refuses keys it does not declare.

---

## `PartnerServiceListRequestedEvent`

Data model: `PartnerServiceListRequestedData`.

- `schema_version`
  - Type: `int`, at least `1`
  - Default: `1`
- `filters`
  - Type: `PartnerServiceListFiltersData`
  - Default: empty filters
  - `name`: `str`, default `None`

## `PartnerServiceListRespondedEvent`

Data model: `PartnerServiceListRespondedData`.

- `schema_version`
  - Type: `int`, at least `1`
  - Default: `1`
- `status`
  - Type: `int`
  - Required: Yes
- `result`
  - Type: `list[PartnerServiceListItemData]`, each with `id` (`UUID`) and `name` (`str`)
  - Default: `None`
- `error`
  - Type: `str`
  - Default: `None`

### Answering a request

```python
response = PartnerServiceListRespondedEvent.answering(request, status=200, items=[(service_id, 'Acme Delivery')])
```

`answering` returns a new event with its own `id_` and `occurred_on`. It copies `correlation_id`, `tenant_id`,
`workspace_id`, `actor_id` and `service_id` from the request, sets the action to `RETRIEVED` and builds `data` from the
arguments. Without `items`, `result` is `None`; `error` is the reason a request failed.
