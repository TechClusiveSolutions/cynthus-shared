# Partner Signal Generator

`PartnerSignalGenerator` turns the two partner events into the two service list signal messages. It is registered in
`SignalGeneratorRegistry.default()` and belongs to feature FT-SR-006. It is a pure function of the event: no I/O, no
clock, no random id and no change to the event. See [signal-generators.md](../../../../signal-generators.md).

---

## Contracts

- `PartnerServiceListRequestedEvent` gives `public.partner.service_list.requested`, through the method `requested`.
  - Sources: `schema_version` from `data.schema_version`, `filters` from `data.filters`.
- `PartnerServiceListRespondedEvent` gives `public.partner.service_list.responded`, through the method `responded`.
  - Sources: `schema_version`, `status`, `result` and `error` from the `data.*` field of the same name.

Both contracts use the lifecycle action `UPDATED`, as the inventory requested and responded messages do, because
`requested` and `responded` are not lifecycle values.

## Envelope

The events are `SignalEvent` classes, which hold ids, not objects. `SignalGenerator.envelope` takes `tenant_id`,
`workspace_id` and `actor_id` straight from the event. The message `event_id` is the id of the event, and its
`timestamp` and the payload `observed_at` are `event.occurred_on`.

## Publishing

```python
publisher = EventMessagePublisher(transport=transport)
message = await publisher.publish(event, access_token)
```

`EventMessagePublisher`, `SignalGeneratorRegistry` and `SignalGenerator.generate` accept an `Event` or a `SignalEvent`.
