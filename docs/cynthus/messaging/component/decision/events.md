# Decision Events

The decision events are `SignalEvent` classes in `cynthus.core.event`. A decision is a new fact, not a read, so
`EventRequestDecisionEvent` allows only the action `CREATED`; any other action is refused when the event is created. A
signal generator maps one event class to one signal, so there is one class for each answer:

- `DecisionEventRequestApprovedEvent`
- `DecisionEventRequestApprovedConditionallyEvent`
- `DecisionEventRequestDeniedEvent`
- `DecisionEventRequestDeniedConditionallyEvent`

All four share the data model `EventRequestDecisionData`, which refuses keys it does not declare. Its fields are those of
`EventRequestDecisionPayload` (see [index.md](index.md)), with each condition as `EventRequestDecisionConditionData`.
The data is held in JSON form, so ids are text.

---

## Deciding a request

```python
event = EventRequestDecisionEvent.deciding(request, decision, service_id=service_id)
```

`deciding` returns the subclass that matches `decision.answer`, with its own `id_` and `occurred_on`, and:

- `correlation_id`, `tenant_id` and `workspace_id` of the event held by `request`. When that event is a full `Event`,
  the ids come from its `tenant` and `workspace`; when it is a `SignalEvent`, they are copied.
- `actor_id` is the requestor: the id of a `User` or `System`, or the UUID itself when the request holds only an id (requires the S10 change, cynthus-shared#186).
- `action` is `CREATED`; `service_id` is the optional service that records the decision.
- `requested_event_type` and `requested_action` come from the event of the request; `event_request_id` and
  `in_reply_to` from the request; the rest from the decision.
