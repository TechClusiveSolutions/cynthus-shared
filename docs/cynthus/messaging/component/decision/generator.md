# Decision Signal Generator

`DecisionSignalGenerator` turns the four decision events into the four decision signal messages. It is registered in
`SignalGeneratorRegistry.default()`. It is a pure function of the event: no I/O, no clock, no random id and no change to
the event. See [signal-generators.md](../../../../signal-generators.md).

---

## Contracts

- `DecisionEventRequestApprovedEvent` gives `public.decision.event_request.approved`, through the method `approved`.
- `DecisionEventRequestApprovedConditionallyEvent` gives `public.decision.event_request.approved_conditionally`, through the
  method `approved_conditionally`.
- `DecisionEventRequestDeniedEvent` gives `public.decision.event_request.denied`, through the method `denied`.
- `DecisionEventRequestDeniedConditionallyEvent` gives `public.decision.event_request.denied_conditionally`, through the method
  `denied_conditionally`.

Every contract uses the lifecycle action `CREATED` and takes each payload field from the `data.*` field of the same name.

## Envelope

The events are `SignalEvent` classes, so `tenant_id`, `workspace_id` and `actor_id` come straight from the event. The
message `event_id` is the id of the event; its `timestamp` and the payload `observed_at` are `event.occurred_on`.

## Publishing

```python
event = EventRequestDecisionEvent.deciding(response.request, response.decision)
message = await EventMessagePublisher(transport=transport).publish(event, access_token)
```
